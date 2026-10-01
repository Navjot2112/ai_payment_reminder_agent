"""Abstract base model — same role as odoo.models.Model / odoo.api.

Every Odoo record carries standard fields: id, create_date, write_date,
and the `active` flag that powers the archive mechanism. This class
gives every model here exactly that.
"""
from database import db
from common import now


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=now, nullable=False)
    write_date = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)  # Odoo "archive" flag
