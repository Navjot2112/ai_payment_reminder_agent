"""REST routes for sale.order — the quotation -> confirmed order flow.

    GET    /api/sales                          list (?state=, ?partner_id=)
    POST   /api/sales                          create a DRAFT quotation (auto-numbered QUOT/xxxx)
    GET    /api/sales/<id>                     fetch one (with lines + totals)
    PUT    /api/sales/<id>                     edit a draft (notes, lines)
    POST   /api/sales/<id>/send                draft -> sent
    POST   /api/sales/<id>/confirm             draft/sent -> sale  (CONFIRM button)
    POST   /api/sales/<id>/cancel              draft/sent -> cancel
    POST   /api/sales/<id>/create-invoice      sale -> creates the invoice (201 + invoice JSON)
"""
from flask import Blueprint, request, jsonify
from database import db
from common import UserError, NotFoundError
from services.sequence import next_by_code
from models.partner import ResPartner
from models.product import ProductProduct
from models.tax import AccountTax
from models.sale import SaleOrder, SaleOrderLine

bp = Blueprint("sales", __name__, url_prefix="/api/sales")


def _get_so(so_id):
    so = db.session.get(SaleOrder, so_id)
    if not so:
        raise NotFoundError(f"Sale order {so_id} not found.")
    return so


def _taxes_from(ids):
    if not ids:
        return []
    return [t for t in (db.session.get(AccountTax, i) for i in ids) if t]


def _make_line(data, seq):
    """Build one sale.order.line — Odoo defaults: price from the product's
    list_price, taxes from the product's tax_ids, unless overridden."""
    product = db.session.get(ProductProduct, data.get("product_id"))
    if not product:
        raise UserError(f"product_id {data.get('product_id')} does not exist.")
    return SaleOrderLine(
        sequence=seq,
        product_id=product.id,
        name=data.get("name"),
        product_uom_qty=float(data.get("qty", data.get("quantity", 1)) or 1),
        price_unit=float(data.get("price_unit", product.list_price) or 0),
        discount=float(data.get("discount", 0) or 0),
        tax_ids=_taxes_from(data.get("tax_ids")) or list(product.tax_ids),
        uom_name=product.uom_name,
    )


@bp.get("")
def list_orders():
    q = SaleOrder.query
    if request.args.get("state"):
        q = q.filter_by(state=request.args["state"])
    if request.args.get("partner_id"):
        q = q.filter_by(partner_id=request.args["partner_id"])
    return jsonify([s.to_dict() for s in q.order_by(SaleOrder.id.desc())])


@bp.post("")
def create_quotation():
    data = request.get_json(force=True) or {}
    partner = db.session.get(ResPartner, data.get("partner_id"))
    if not partner:
        raise UserError("partner_id must reference an existing customer.")
    lines_data = data.get("lines") or []
    if not lines_data:
        raise UserError("At least one line is required.")

    so = SaleOrder(
        name=next_by_code("sale_order"),   # <- QUOT/0001, just like Odoo
        partner_id=partner.id,
        notes=data.get("notes"),
    )
    for i, ld in enumerate(lines_data, 1):
        so.order_line.append(_make_line(ld, i * 10))
    db.session.add(so)
    db.session.commit()
    return jsonify(so.to_dict()), 201


@bp.get("/<int:so_id>")
def get_order(so_id):
    return jsonify(_get_so(so_id).to_dict())


@bp.put("/<int:so_id>")
def update_quotation(so_id):
    so = _get_so(so_id)
    if so.state != "draft":
        raise UserError(f"Only a draft quotation can be edited (state={so.state}).")
    data = request.get_json(force=True) or {}
    if "notes" in data:
        so.notes = data["notes"]
    if "lines" in data:
        for l in list(so.order_line):
            db.session.delete(l)
        for i, ld in enumerate(data["lines"] or [], 1):
            so.order_line.append(_make_line(ld, i * 10))
    db.session.commit()
    return jsonify(so.to_dict())


@bp.post("/<int:so_id>/send")
def send_quotation(so_id):
    _get_so(so_id).action_quotation_sent()
    return jsonify({"ok": True})


@bp.post("/<int:so_id>/confirm")
def confirm_order(so_id):
    so = _get_so(so_id).action_confirm()
    return jsonify({"ok": True, "sale_order": _get_so(so_id).to_dict()})


@bp.post("/<int:so_id>/cancel")
def cancel_order(so_id):
    _get_so(so_id).action_cancel()
    return jsonify({"ok": True})


@bp.post("/<int:so_id>/create-invoice")
def create_invoice(so_id):
    move = _get_so(so_id).create_invoice()
    return jsonify(move.to_dict()), 201
