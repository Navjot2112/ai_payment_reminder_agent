"""Small shared helpers — mirrors Odoo's exceptions and tools."""
from datetime import datetime, date


class UserError(Exception):
    """Business rule violation (direct port of odoo.exceptions.UserError).

    Flask's error handler in app.py converts this to an HTTP 400 with
    the message as JSON: {"error": "..."}.
    """


class NotFoundError(Exception):
    """Record does not exist -> HTTP 404 (Odoo has no direct equivalent;
    the ORM just returns an empty recordset — we make it explicit here)."""


def now():
    return datetime.utcnow()


def today():
    return date.today()
