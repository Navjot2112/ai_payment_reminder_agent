"""Import every model so `db.create_all()` knows about all tables.

This file is the equivalent of an Odoo addon's models/__init__.py:
the module "manifest" that tells the framework which models exist.
"""
from .base import Base
from .partner import ResPartner
from .tax import AccountTax
from .sequence import IrSequence
from .product import ProductProduct
from .sale import SaleOrder, SaleOrderLine
from .account_move import AccountMove, AccountMoveLine
from .payment import AccountPayment

__all__ = [
    "Base",
    "ResPartner",
    "AccountTax",
    "IrSequence",
    "ProductProduct",
    "SaleOrder",
    "SaleOrderLine",
    "AccountMove",
    "AccountMoveLine",
    "AccountPayment",
]
