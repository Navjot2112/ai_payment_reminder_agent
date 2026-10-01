"""account.tax — the tax records the tax engine uses (VAT / GST lines).

Odoo equivalent: odoo/addons/account/models/account_tax.py
"""
from database import db
from models.base import Base


class AccountTax(Base):
    __tablename__ = "account_tax"

    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)  # percent
    # Port of Odoo's `tax_base` field:
    #   total_excluded -> shown price is EXCLUSIVE of tax, tax is added on top
    #   total_included -> shown price is INCLUSIVE of tax, tax is extracted
    tax_base = db.Column(db.String, default="total_excluded", nullable=False)
    sequence = db.Column(db.Integer, default=10)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "tax_base": self.tax_base,
        }
