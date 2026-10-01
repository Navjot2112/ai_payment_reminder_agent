"""REST routes for account.move (invoices) and payments.

    GET    /api/invoices                       list (?state=, ?partner_id=)
    GET    /api/invoices/<id>                  fetch one (lines + payments + totals)
    POST   /api/invoices/<id>/post             draft -> posted   (VALIDATE button)
    POST   /api/invoices/<id>/payment         register payment  -> paid | partial
    POST   /api/invoices/<id>/cancel          draft -> cancel
"""
from flask import Blueprint, request, jsonify
from database import db
from common import UserError, NotFoundError
from models.account_move import AccountMove

bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


def _get_move(move_id):
    move = db.session.get(AccountMove, move_id)
    if not move:
        raise NotFoundError(f"Invoice {move_id} not found.")
    return move


@bp.get("")
def list_invoices():
    q = AccountMove.query
    if request.args.get("state"):
        q = q.filter_by(state=request.args["state"])
    if request.args.get("partner_id"):
        q = q.filter_by(partner_id=request.args["partner_id"])
    return jsonify([m.to_dict() for m in q.order_by(AccountMove.id.desc())])


@bp.get("/<int:move_id>")
def get_invoice(move_id):
    return jsonify(_get_move(move_id).to_dict())


@bp.post("/<int:move_id>/post")
def post_invoice(move_id):
    _get_move(move_id).post()
    return jsonify({"ok": True, "invoice": _get_move(move_id).to_dict()})


@bp.post("/<int:move_id>/payment")
def register_payment(move_id):
    data = request.get_json(force=True) or {}
    move = _get_move(move_id)
    payment = move.register_payment(
        amount=data.get("amount"),
        payment_method=data.get("payment_method", "bank"),
        communication=data.get("communication"),
    )
    return jsonify({
        "ok": True,
        "payment": payment.to_dict(),
        "invoice": _get_move(move_id).to_dict(),
    })


@bp.post("/<int:move_id>/cancel")
def cancel_invoice(move_id):
    _get_move(move_id).cancel()
    return jsonify({"ok": True})
