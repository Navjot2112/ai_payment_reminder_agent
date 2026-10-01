"""res.partner — customers and vendors.

Odoo equivalent: odoo/addons/base/models/res_partner.py
"""
from database import db
from models.base import Base


class ResPartner(Base):
    __tablename__ = "res_partner"

    name = db.Column(db.String, nullable=False, index=True)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.String)
    country = db.Column(db.String)
    is_company = db.Column(db.Boolean, default=False)
    # Odoo uses customer_rank / vendor_rank to control which sales features a
    # contact unlocks. 1 = enabled.
    customer_rank = db.Column(db.Boolean, default=True)
    vendor_rank = db.Column(db.Boolean, default=False)

    # one2many, like Odoo's sale_order_ids / invoice_ids on res.partner
    sale_orders = db.relationship("SaleOrder", backref="partner", lazy="dynamic")
    invoices = db.relationship("AccountMove", backref="partner", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
            "country": self.country,
        }
