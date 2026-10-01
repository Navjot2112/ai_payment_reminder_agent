"""SQLAlchemy engine — the equivalent of Odoo's ORM registry.

In Odoo you access models through `self.env['model']`. Here every
`db.Model` class registered on this metadata plays that role:
one class = one table = one model, queryable anywhere via
`Model.query` (scoped to the current Flask app context).
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
