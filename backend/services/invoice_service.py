"""create_invoice() — Python port of sale.order.create_invoice().

This is exactly what happens in Odoo when you click "Create Invoice" on a
CONFIRMED sale order:

1. an account.move of type out_invoice is created,
2. one move line per sale order line (discount folded into the unit price,
   taxes copied from the SO line),
3. the source document number is kept as `ref` (e.g. QUOT/2026-0001),
4. the sale order's invoiced counter is updated.
"""
from common import UserError, today
from database import db
from models.account_move import AccountMove, AccountMoveLine
from services.sequence import next_by_code


def create_invoice_from_so(so):
    """Create the customer invoice for a confirmed sale order."""
    if so.state != "sale":
        raise UserError(
            f"Sale order {so.name} must be CONFIRMED (state 'sale') before invoicing."
        )
    if not so.order_line:
        raise UserError(f"Sale order {so.name} has no lines to invoice.")

    move = AccountMove(
        name=next_by_code("account_invoice"),
        move_type="out_invoice",
        partner_id=so.partner_id,
        ref=so.name,          # links the invoice back to the quotation
        date=today(),
    )
    for line in so.order_line:
        # Odoo applies the discount to the unit price when moving to the invoice
        discounted_unit = round(line.price_unit * (1 - (line.discount or 0) / 100.0), 2)
        move.invoice_line_ids.append(AccountMoveLine(
            product_id=line.product_id,
            name=line.name or (line.product.name if line.product else "Sale"),
            quantity=line.product_uom_qty,
            price_unit=discounted_unit,
            tax_ids=list(line.tax_ids),
        ))

    # Update the SO's invoicing status (Odoo: invoice_status computed field)
    so.invoiced_amount = round(so.invoiced_amount + move.total_amount, 2)
    so.invoiced_count += 1

    db.session.add(move)
    db.session.commit()
    return move
