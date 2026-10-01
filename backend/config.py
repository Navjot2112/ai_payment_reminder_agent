"""Central configuration — the Odoo-style single place for environment settings.

Everything that changes between environments lives here and can be
overridden with environment variables, exactly like Odoo's config.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite by default (zero setup, one file).
# Switch to Postgres later by setting: DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "sales.db")
)

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# LLM settings used by the AI stubs (see ai/llm.py)
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
