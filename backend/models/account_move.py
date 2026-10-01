"""account.move + account.move.line — invoices.

Odoo equivalent: odoo/addons/account/models/account_move.py

State machine (identical to Odoo):

    draft  ->  posted (validated)  ->  paid
                 \\------> partial (partially paid)
    draft  ->  cancel
"""
from database import db
from models.base import Base
from models.payment import AccountPayment
from common import UserError, today

# many2many invoice line <-> tax (Odoo: account.move.line.tax_ids)
move_line_tax = db.Table(
    "account_move_line_tax",
    db.Column("line_id", db.ForeignKey("account_move_line.id"), primary_key=True),
    db.Column("tax_id", db.ForeignKey("account_tax.id"), primary_key=True),
)


class AccountMove(Base):
    __tablename__ = "account_move"

    name = db.Column(db.String, unique=True, index=True)   # INV/0001 (from ir.sequence)
    move_type = db.Column(db.String, default="out_invoice", nullable=False)
    # out_invoice = customer invoice | out_refund = customer refund
    partner_id = db.Column(db.Integer, db.ForeignKey("res_partner.id"), nullable=False)
    ref = db.Column(db.String)   # source document, e.g. QUOT/2026-0003 (Odoo: ref)
    date = db.Column(db.Date, default=today, nullable=False)
    state = db.Column(db.String, default="draft", nullable=False)
    # draft | posted | partial | paid | cancel

    invoice_line_ids = db.relationship(
        "AccountMoveLine",
        backref="move",
        cascade="all, delete-orphan",
        order_by="AccountMoveLine.sequence",
    )
    payments = db.relationship(
        "AccountPayment", backref="move", cascade="all, delete-orphan"
    )

    # ------------------------------------------------ computed
    @property
    def subtotal(self):
        return round(sum(l.price_subtotal for l in self.invoice_line_ids), 2)

    @property
    def tax_total(self):
        return round(sum(l.tax_amount for l in self.invoice_line_ids), 2)

    @property
    def total_amount(self):
        return round(self.subtotal + self.tax_total, 2)

    @property
    def amount_residual(self):
        """Amount still owed (Odoo: amount_residual)."""
        paid = sum(p.amount for p in self.payments)
        return round(max(self.total_amount - paid, 0), 2)

    # ------------------------------------------------ model methods

    def post(self):
        """Validate the invoice (Odoo: action_post). Draft -> posted."""
        if self.state != "draft":
            raise UserError(f"Invoice {self.name} is not in draft state.")
        if not self.invoice_line_ids:
            raise UserError("Cannot post an invoice without lines.")
        self.state = "posted"
        db.session.commit()
        return True

    def register_payment(self, amount=None, payment_method="bank", communication=None):
        """Register money received (Odoo: register payment from the invoice).

        Full amount -> state 'paid'; partial amount -> state 'partial'.
        """
        if self.state not in ("posted", "partial"):
            raise UserError("Only a posted invoice can receive payments.")
        amount = amount if amount is not None else self.amount_residual
        if amount is None or amount <= 0:
            raise UserError("Payment amount must be positive.")
        payment = AccountPayment(
            move=self,
            amount=round(amount, 2),
            payment_method=payment_method,
            communication=communication,
            date=today(),
        )
        self.state = "paid" if (self.amount_residual - amount) <= 0.005 else "partial"
        db.session.add(payment)
        db.session.commit()
        return payment

    def cancel(self):
        if self.payments:
            raise UserError("A paid invoice cannot be cancelled; reverse it instead.")
        self.state = "cancel"
        db.session.commit()
        return True

    def to_dict(self, with_lines=True):
        d = {
            "id": self.id,
            "name": self.name,
            "move_type": self.move_type,
            "partner_id": self.partner_id,
            "partner": self.partner.name if self.partner else None,
            "ref": self.ref,
            "date": self.date.isoformat() if self.date else None,
            "state": self.state,
            "subtotal": self.subtotal,
            "tax_total": self.tax_total,
            "total_amount": self.total_amount,
            "amount_residual": self.amount_residual,
            "payments": [p.to_dict() for p in self.payments],
        }
        if with_lines:
            d["lines"] = [l.to_dict() for l in self.invoice_line_ids]
        return d


class AccountMoveLine(Base):
    __tablename__ = "account_move_line"

    sequence = db.Column(db.Integer, default=10)
    move_id = db.Column(db.Integer, db.ForeignKey("account_move.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product_product.id"))
    name = db.Column(db.String, nullable=False)   # Odoo: label on the invoice
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    price_unit = db.Column(db.Float, nullable=False, default=0.0)
    account_type = db.Column(db.String, default="income")  # income | tax | receivable

    product = db.relationship("ProductProduct")
    tax_ids = db.relationship("AccountTax", secondary=move_line_tax, lazy="subquery")

    @property
    def price_subtotal(self):
        return round(self.quantity * self.price_unit, 2)

    @property
    def tax_amount(self):
        from services.tax import compute_taxes
        return compute_taxes(self.price_subtotal, list(self.tax_ids))[0]

    @property
    def price_total(self):
        return round(self.price_subtotal + self.tax_amount, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product": self.product.name if self.product else None,
            "name": self.name,
            "quantity": self.quantity,
            "price_unit": self.price_unit,
            "subtotal": self.price_subtotal,
            "tax_amount": self.tax_amount,
            "total": self.price_total,
            "taxes": [t.name for t in self.tax_ids],
        }
