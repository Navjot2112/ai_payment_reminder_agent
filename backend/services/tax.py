"""Tax engine — Python port of Odoo's account.tax computation.

Odoo computes taxes per line using the tax's `tax_base` behaviour. We keep
the same two modes:

* total_excluded (price_untaxed): the line price does NOT include tax,
  so  tax = base * rate,  total = base + tax.
* total_included (price_tax_included): the line price INCLUDES tax,
  so  tax = base - base / (1 + rate).
"""


def compute_taxes(base_amount, taxes):
    """Compute tax for a base amount and a list of AccountTax records.

    Returns:
        (total_tax: float, tax_details: list[dict])
        tax_details: [{"tax": name, "base": float, "amount": float}, ...]
    """
    total_tax = 0.0
    details = []
    for tax in taxes:
        rate = tax.amount / 100.0
        if rate == 0:
            tax_amount = 0.0
        elif tax.tax_base == "total_included":
            tax_amount = round(base_amount - base_amount / (1 + rate), 2)
        else:
            tax_amount = round(base_amount * rate, 2)
        total_tax = round(total_tax + tax_amount, 2)
        details.append({
            "tax": tax.name,
            "base": round(base_amount, 2),
            "amount": tax_amount,
        })
    return total_tax, details
