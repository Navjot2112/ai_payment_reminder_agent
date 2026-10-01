"""Seed data — the equivalent of Odoo demo data.

Runs once at startup (guarded by a count check) so the demo flow works
immediately: taxes, one customer, a few products.
"""
from database import db
from models.tax import AccountTax
from models.partner import ResPartner
from models.product import ProductProduct


def seed():
    if AccountTax.query.count():
        return  # already seeded

    vat = AccountTax(name="VAT 18%", amount=18.0, tax_base="total_excluded")
    gst = AccountTax(name="GST 5%", amount=5.0, tax_base="total_excluded")

    partner = ResPartner(
        name="Acme Industries",
        email="accounts@acme.com",
        phone="+91 98765 43210",
        city="Mumbai",
        state="MH",
        zip="400001",
        country="India",
    )

    products = [
        ProductProduct(
            name="LED Panel 40W",
            default_code="LED-40W",
            description="40W LED panel light, 4000K daylight",
            list_price=1850.0,
            standard_price=1100.0,
            tax_ids=[vat],
        ),
        ProductProduct(
            name="Industrial Fan 1200mm",
            default_code="FAN-1200",
            description="1200mm industrial fan, 240V",
            list_price=2400.0,
            standard_price=1600.0,
            tax_ids=[vat],
        ),
        ProductProduct(
            name="Installation Service",
            default_code="SVC-INSTALL",
            description="On-site installation, per unit",
            type="service",
            list_price=500.0,
            standard_price=0.0,
            tax_ids=[gst],
        ),
    ]
    db.session.add_all([vat, gst, partner, *products])
    db.session.commit()
