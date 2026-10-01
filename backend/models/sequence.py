"""ir.sequence — automatic document numbering (QUOT/0001, INV/0002, ...).

Odoo equivalent: odoo/addons/base/models/ir_sequence.py, method next_by_id().
Every new quotation / invoice grabs the next number from its sequence,
which is exactly how Odoo numbers documents.
"""
from database import db
from models.base import Base


class IrSequence(Base):
    __tablename__ = "ir_sequence"

    name = db.Column(db.String, nullable=False)
    # 'code' is what other models reference, e.g. 'sale_order', 'account_invoice'
    code = db.Column(db.String, unique=True, index=True, nullable=False)
    prefix = db.Column(db.String, default="")
    suffix = db.Column(db.String, default="")
    padding = db.Column(db.Integer, default=4)
    number_next = db.Column(db.Integer, default=1, nullable=False)
    number_increment = db.Column(db.Integer, default=1, nullable=False)

    def next_by_id(self):
        """Return the next formatted number and advance the counter.

        Mirrors ir.sequence.next_by_id() — returns e.g. 'QUOT/0007'.
        """
        number = self.number_next
        self.number_next += self.number_increment
        return "{}{:0{}d}{}".format(self.prefix, number, self.padding, self.suffix or "")
