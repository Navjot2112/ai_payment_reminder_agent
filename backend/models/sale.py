"""sale.order + sale.order.line — the quotation -> confirmed order flow.

Odoo equivalent: odoo/addons/sale/models/sale.py

State machine (identical to Odoo):

    draft  ->  sent  ->  sale (confirmed)  ->  done
      \\-----------> cancel

* draft : you can edit lines, prices, discount
* sent  : quotation marked as "sent to customer"
* sale  : CONFIRMED. No more editing; now you can create invoices
* cancel: voided (only before confirmation)
"""
from database import db
from models.base import Base
from common import UserError, today

# many2many SO line <-> tax (Odoo: sale.order.line.tax_id)
so_line_tax = db.Table(
    "sale_order_line_tax",
    db.Column("line_id", db.ForeignKey("sale_order_line.id"), primary_key=True),
    db.Column("tax_id", db.ForeignKey("account_tax.id"), primary_key=True),
)


class SaleOrder(Base):
    __tablename__ = "sale_order"

    name = db.Column(db.String, unique=True, index=True)   # QUOT/0001 (from ir.sequence)
    partner_id = db.Column(db.Integer, db.ForeignKey("res_partner.id"), nullable=False)
    state = db.Column(db.String, default="draft", nullable=False)
    date_order = db.Column(db.Date)                        # set on confirmation
    notes = db.Column(db.Text)
    # Odoo: invoiced_amount / invoice_status on sale.order
    invoiced_amount = db.Column(db.Float, default=0.0)
    invoiced_count = db.Column(db.Integer, default=0)

    order_line = db.relationship(
        "SaleOrderLine",
        backref="order",
        cascade="all, delete-orphan",
        order_by="SaleOrderLine.sequence",
    )

    # ------------------------------------------------ computed fields
    # (Odoo: @api.depends / @api.computed on sale.order)
    @property
    def subtotal(self):
        return round(sum(l.price_subtotal for l in self.order_line), 2)

    @property
    def tax_total(self):
        return round(sum(l.tax_amount for l in self.order_line), 2)

    @property
    def total_amount(self):
        return round(self.subtotal + self.tax_total, 2)

    @property
    def invoice_status(self):
        total = self.total_amount
        if self.invoiced_amount <= 0:
            return "no"
        if abs(self.invoiced_amount - total) < 0.01:
            return "invoiced"
        return "over_invoiced" if self.invoiced_amount > total else "partially_invoiced"

    # ------------------------------------------------ model methods
    # (Odoo: regular methods, exposed as buttons in the client UI)

    def action_quotation_sent(self):
        if self.state != "draft":
            raise UserError("Only a draft quotation can be marked as sent.")
        self.state = "sent"
        db.session.commit()
        return True

    def action_confirm(self):
        """Draft/sent -> sale. This is the 'Confirm' button in Odoo."""
        if self.state not in ("draft", "sent"):
            raise UserError(
                f"Quotation {self.name} is in state '{self.state}' and cannot be confirmed."
            )
        self.state = "sale"
        self.date_order = today()
        db.session.commit()
        return True

    def action_cancel(self):
        if self.state in ("sale", "done"):
            raise UserError("A confirmed order cannot be cancelled; issue a refund instead.")
        self.state = "cancel"
        db.session.commit()
        return True

    def create_invoice(self):
        """Mirror of sale.order.create_invoice() -> account.move (out_invoice)."""
        from services.invoice_service import create_invoice_from_so
        return create_invoice_from_so(self)

    def to_dict(self, with_lines=True):
        d = {
            "id": self.id,
            "name": self.name,
            "partner_id": self.partner_id,
            "partner": self.partner.name if self.partner else None,
            "state": self.state,
            "date_order": self.date_order.isoformat() if self.date_order else None,
            "notes": self.notes,
            "subtotal": self.subtotal,
            "tax_total": self.tax_total,
            "total_amount": self.total_amount,
            "invoice_status": self.invoice_status,
            "invoiced_amount": self.invoiced_amount,
        }
        if with_lines:
            d["lines"] = [l.to_dict() for l in self.order_line]
        return d


class SaleOrderLine(Base):
    __tablename__ = "sale_order_line"

    sequence = db.Column(db.Integer, default=10)
    order_id = db.Column(db.Integer, db.ForeignKey("sale_order.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product_product.id"), nullable=False)
    name = db.Column(db.String)   # line description override (Odoo: line description)
    product_uom_qty = db.Column(db.Float, nullable=False, default=1.0)
    price_unit = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, default=0.0)   # percent, 0-100 (Odoo: discount)
    uom_name = db.Column(db.String, default="Units")

    product = db.relationship("ProductProduct")
    tax_ids = db.relationship("AccountTax", secondary=so_line_tax, lazy="subquery")

    # ------------------------------------------------ computed (Odoo: _compute_price_subtotal etc.)
    @property
    def base_amount(self):
        """price_unit * qty * (1 - discount%) — Odoo's discount-aware base."""
        return self.price_unit * self.product_uom_qty * (1 - (self.discount or 0) / 100.0)

    @property
    def price_subtotal(self):
        return round(self.base_amount, 2)

    @property
    def tax_amount(self):
        from services.tax import compute_taxes
        return compute_taxes(self.base_amount, list(self.tax_ids))[0]

    @property
    def price_total(self):
        return round(self.price_subtotal + self.tax_amount, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product": self.product.name if self.product else None,
            "name": self.name or (self.product.name if self.product else ""),
            "qty": self.product_uom_qty,
            "price_unit": self.price_unit,
            "discount": self.discount,
            "subtotal": self.price_subtotal,
            "tax_amount": self.tax_amount,
            "total": self.price_total,
            "taxes": [t.name for t in self.tax_ids],
        }
