"""product.product — the product catalogue.

Odoo equivalent: odoo/addons/product/models/product.py.
In Odoo, product.template holds the shared data and product.product is the
sellable unit; here both are merged into ONE table to keep the demo lean
(the field names are kept Odoo-accurate so you can map back 1:1).
"""
from database import db
from models.base import Base

# many2many product <-> tax (Odoo: product.template.tax_ids)
product_tax = db.Table(
    "product_tax",
    db.Column("product_id", db.ForeignKey("product_product.id"), primary_key=True),
    db.Column("tax_id", db.ForeignKey("account_tax.id"), primary_key=True),
)


class ProductProduct(Base):
    __tablename__ = "product_product"

    name = db.Column(db.String, nullable=False, index=True)    # Odoo: display_name
    default_code = db.Column(db.String, index=True)            # Odoo: SKU
    description = db.Column(db.Text)                           # Odoo: description_sale
    type = db.Column(db.String, default="consu", nullable=False)  # consu | service
    list_price = db.Column(db.Float, default=0.0, nullable=False)      # sale price
    standard_price = db.Column(db.Float, default=0.0, nullable=False)  # cost price
    uom_name = db.Column(db.String, default="Units")           # Odoo: uom_id.name
    margin = db.Column(db.Float, default=0.0)                  # list_price - standard_price

    # Many2many — the default taxes applied when a line uses this product
    tax_ids = db.relationship("AccountTax", secondary=product_tax, lazy="subquery")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.default_code,
            "description": self.description,
            "type": self.type,
            "list_price": self.list_price,
            "standard_price": self.standard_price,
            "margin": round(self.list_price - self.standard_price, 2),
            "uom": self.uom_name,
            "taxes": [t.name for t in self.tax_ids],
            "active": self.active,
        }
