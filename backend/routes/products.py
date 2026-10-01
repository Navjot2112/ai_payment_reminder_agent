"""REST routes for product.product (the catalogue).

    GET    /api/products            list (filter: ?name=, ?active=)
    POST   /api/products            create product
    GET    /api/products/<id>       fetch one
    PUT    /api/products/<id>       update
    DELETE /api/products/<id>       archive (Odoo-style: active=False, not deleted)
"""
from flask import Blueprint, request, jsonify
from database import db
from common import UserError, NotFoundError
from models.product import ProductProduct
from models.tax import AccountTax

bp = Blueprint("products", __name__, url_prefix="/api/products")


def _taxes_from(ids):
    if not ids:
        return []
    return [t for t in (db.session.get(AccountTax, i) for i in ids) if t]


@bp.get("")
def list_products():
    q = ProductProduct.query
    if request.args.get("name"):
        q = q.filter(ProductProduct.name.ilike(f"%{request.args['name']}%"))
    if request.args.get("active") is not None:
        q = q.filter_by(active=request.args["active"] == "true")
    return jsonify([p.to_dict() for p in q.order_by(ProductProduct.name)])


@bp.post("")
def create_product():
    data = request.get_json(force=True) or {}
    if not data.get("name"):
        raise UserError("Field 'name' is required.")
    p = ProductProduct(
        name=data["name"],
        default_code=data.get("default_code"),
        description=data.get("description"),
        type=data.get("type", "consu"),
        list_price=float(data.get("list_price", 0) or 0),
        standard_price=float(data.get("standard_price", 0) or 0),
        uom_name=data.get("uom_name", "Units"),
        tax_ids=_taxes_from(data.get("tax_ids")),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.get("/<int:product_id>")
def get_product(product_id):
    p = db.session.get(ProductProduct, product_id)
    if not p:
        raise NotFoundError(f"Product {product_id} not found.")
    return jsonify(p.to_dict())


@bp.put("/<int:product_id>")
def update_product(product_id):
    p = db.session.get(ProductProduct, product_id)
    if not p:
        raise NotFoundError(f"Product {product_id} not found.")
    data = request.get_json(force=True) or {}
    for field in ("name", "default_code", "description", "type", "uom_name"):
        if field in data:
            setattr(p, field, data[field])
    if "list_price" in data:
        p.list_price = float(data["list_price"])
    if "standard_price" in data:
        p.standard_price = float(data["standard_price"])
    if "tax_ids" in data:
        p.tax_ids = _taxes_from(data["tax_ids"])
    db.session.commit()
    return jsonify(p.to_dict())


@bp.delete("/<int:product_id>")
def archive_product(product_id):
    """Odoo-style archive: the row stays (history is preserved), active=False."""
    p = db.session.get(ProductProduct, product_id)
    if not p:
        raise NotFoundError(f"Product {product_id} not found.")
    p.active = False
    db.session.commit()
    return jsonify({"id": p.id, "name": p.name, "archived": True})
