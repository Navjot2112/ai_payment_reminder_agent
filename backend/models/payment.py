"""account.payment — money received against an invoice.

Odoo equivalent: odoo/addons/account/models/payment.py
"""
from database import db
from models.base import Base
from common import today


class AccountPayment(Base):
    __tablename__ = "account_payment"

    move_id = db.Column(db.Integer, db.ForeignKey("account_move.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String, default="bank")  # bank | cash | card | upi
    communication = db.Column(db.String)   # reference / note
    date = db.Column(db.Date, default=today, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "communication": self.communication,
            "date": self.date.isoformat() if self.date else None,
        }
