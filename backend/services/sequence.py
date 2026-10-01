"""Document numbering — Python port of ir.sequence.next_by_id().

Odoo looks up a sequence by code (e.g. 'sale.order' -> QUOT/%(year)s/%04d).
Here we keep it simple but behaviour-identical: one row per code, a counter
that always advances, and formatted output like 'QUOT/0001', 'INV/0002'.
"""
from database import db
from models.sequence import IrSequence

DEFAULTS = {
    "sale_order": {"prefix": "QUOT/", "padding": 4},
    "account_invoice": {"prefix": "INV/", "padding": 4},
}


def next_by_code(code):
    """Return the next number for `code`, creating the sequence if missing.

    Example: next_by_code('sale_order') -> 'QUOT/0001'
    """
    seq = IrSequence.query.filter_by(code=code).first()
    if seq is None:
        cfg = DEFAULTS.get(code, {"prefix": code.upper() + "/", "padding": 4})
        seq = IrSequence(name=code, code=code, prefix=cfg["prefix"], padding=cfg["padding"])
        db.session.add(seq)
        db.session.commit()
    number = seq.next_by_id()
    db.session.commit()
    return number
