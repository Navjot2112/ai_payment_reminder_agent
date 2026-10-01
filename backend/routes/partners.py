"""REST routes for res.partner (customers).

    GET    /api/partners            list (filter: ?name=)
    POST   /api/partners            create customer
    GET    /api/partners/<id>       fetch one
    PUT    /api/partners/<id>       update
"""
from flask import Blueprint, request, jsonify
from database import db
from common import UserError, NotFoundError
from models.partner import ResPartner

bp = Blueprint("partners", __name__, url_prefix="/api/partners")

FIELDS = ("name", "email", "phone", "city", "state", "zip", "country", "is_company")


@bp.get("")
def list_partners():
    q = ResPartner.query
    if request.args.get("name"):
        q = q.filter(ResPartner.name.ilike(f"%{request.args['name']}%"))
    return jsonify([p.to_dict() for p in q.order_by(ResPartner.name)])


@bp.post("")
def create_partner():
    data = request.get_json(force=True) or {}
    if not data.get("name"):
        raise UserError("Field 'name' is required.")
    p = ResPartner(**{k: data.get(k) for k in FIELDS if k in data})
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.get("/<int:partner_id>")
def get_partner(partner_id):
    p = db.session.get(ResPartner, partner_id)
    if not p:
        raise NotFoundError(f"Partner {partner_id} not found.")
    return jsonify(p.to_dict())


@bp.put("/<int:partner_id>")
def update_partner(partner_id):
    p = db.session.get(ResPartner, partner_id)
    if not p:
        raise NotFoundError(f"Partner {partner_id} not found.")
    data = request.get_json(force=True) or {}
    for k in FIELDS:
        if k in data:
            setattr(p, k, data[k])
    db.session.commit()
    return jsonify(p.to_dict())
