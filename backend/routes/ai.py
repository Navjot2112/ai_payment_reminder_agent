"""REST routes for the AI layer.

    POST /api/ai/draft-quotation
         {
           "text": "3 x LED Panel @ 1850 and 20 Industrial Fan 1200mm",
           "partner_id": 1,            (optional -> first customer)
           "auto_create_products": true (optional)
         }
         The agent parses the text and executes tool calls against the real
         business logic:
           1. product.lookup(name)
           2. product.create(name)      <- only if missing AND auto_create
           3. sale.order.create + sale.add_line(...)
         Response: the real draft quotation (QUOT/xxxx) + `agent_steps`
         (the trace of every tool call — display it in your UI, it's your
         'agentic AI' showcase).

    GET  /api/ai/health
"""
from flask import Blueprint, request, jsonify
from database import db
from common import UserError
from services.sequence import next_by_code
from ai.quotation_agent import extract_order_items
from models.partner import ResPartner
from models.product import ProductProduct
from models.sale import SaleOrder, SaleOrderLine

bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@bp.post("/draft-quotation")
def draft_quotation():
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        raise UserError("Field 'text' is required.")
    auto_create = data.get("auto_create_products", True)

    partner = (
        db.session.get(ResPartner, data["partner_id"])
        if data.get("partner_id")
        else ResPartner.query.order_by(ResPartner.id).first()
    )
    if not partner:
        raise UserError("No customer found — create one first (POST /api/partners).")

    # ---- Step 1: the "brain" (rule-based today, LLM tomorrow)
    items = extract_order_items(text)
    if not items:
        raise UserError("Could not extract any products from the text.")

    # ---- Step 2: execute tool calls against the real business logic
    # (name is assigned only right before commit, so a failed parse does not
    #  burn a QUOT number from the sequence)
    so = SaleOrder(partner_id=partner.id, notes=f"[AI draft] {text}")
    agent_steps = [f"tool: text.parse(...) -> {len(items)} items"]
    for i, item in enumerate(items, 1):
        product = ProductProduct.query.filter(
            ProductProduct.name.ilike(item["product_name"])
        ).first()
        if product is None:
            # A bare noun phrase with no quantity and no price is ambiguous
            # ("hello how are you") — don't auto-create it as a product.
            if not item.get("has_spec"):
                agent_steps.append(
                    f"skip: '{item['product_name']}' (no quantity/price, not a known product)"
                )
                continue
            if not auto_create:
                raise UserError(
                    f"Product '{item['product_name']}' not found and auto_create_products=false."
                )
            product = ProductProduct(
                name=item["product_name"],
                list_price=item["price_unit"] or 0.0,
            )
            db.session.add(product)
            db.session.flush()
            agent_steps.append(
                f"tool: product.create('{item['product_name']}') -> id {product.id}"
            )
        price = item["price_unit"] if item["price_unit"] is not None else product.list_price
        so.order_line.append(SaleOrderLine(
            sequence=i * 10,
            product_id=product.id,
            product_uom_qty=item["quantity"],
            price_unit=price,
            tax_ids=list(product.tax_ids),
            uom_name=product.uom_name,
        ))
        agent_steps.append(
            f"tool: sale.add_line('{product.name}' x {item['quantity']} @ {price})"
        )

    if not so.order_line:
        db.session.rollback()
        raise UserError(
            "No usable order lines found in the text. Try e.g. '3 x LED Panel @ 1850, 20 fans'."
        )
    so.name = next_by_code("sale_order")
    db.session.add(so)
    db.session.commit()
    return jsonify({"quotation": so.to_dict(), "agent_steps": agent_steps}), 201


@bp.get("/health")
def ai_health():
    return jsonify({"status": "ok", "brain": "rule-based (LLM hook: ai/llm.py)"})
