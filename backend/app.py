"""Entry point — run with:  python app.py   (or: flask --app app run)

Serves the full sales pipeline as a JSON API (UI-agnostic):

    products  ->  partners  ->  quotations (sale.order)
                ->  invoices (account.move)  ->  payments

This is a Python port of Odoo's core product/sale/account models:
same model names, same states, same button actions — no Odoo runtime needed.
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import DATABASE_URL, SECRET_KEY
from database import db
import models  # noqa: F401  (register all models on the metadata)
from common import UserError, NotFoundError
from seed import seed
from routes import partners as r_partners
from routes import products as r_products
from routes import sales as r_sales
from routes import invoices as r_invoices
from routes import ai as r_ai


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = SECRET_KEY

    db.init_app(app)
    CORS(app)  # your frontend (any port/origin) can call this API directly

    app.register_blueprint(r_partners.bp)
    app.register_blueprint(r_products.bp)
    app.register_blueprint(r_sales.bp)
    app.register_blueprint(r_invoices.bp)
    app.register_blueprint(r_ai.bp)

    @app.errorhandler(UserError)
    def handle_user_error(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify(error=str(e)), 404

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="sales-pipeline")

    with app.app_context():
        db.create_all()
        seed()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
