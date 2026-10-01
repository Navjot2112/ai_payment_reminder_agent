"""Agentic quotation drafter.

Phase 1 (works TODAY, no API key): a rule-based extractor pulls items out
of free text ("3 x LED Panel @ 1850, 10 fans"). The route then executes
those as TOOL CALLS against the real business logic:
    product.lookup -> (if missing and allowed) product.create -> sale.add_line
That loop — decide -> tool call -> observe -> next step — is exactly how
an LLM agent runs.

Phase 2 (your next step): replace `extract_order_items` with an LLM
structured-output call (ai/llm.complete_structured). The tool-execution
pipeline in routes/ai.py stays unchanged — only the "brain" changes.
"""
import re

# stop-words so "total 1250" / "thanks" don't get parsed as products
_STOP = {"total", "grand total", "subtotal", "tax", "amount", "invoice",
         "order", "please", "thanks", "thank you", "i", "want", "need"}


def extract_order_items(text):
    """Extract [{product_name, quantity, price_unit}] from free text.

    Understands, per line / comma / 'and' segment:
        '3 x LED Panel @ 1850'
        '20 LED Panel'
        'LED Panel @ 500'
        '500 per LED Panel'
    price_unit is None when not stated (the caller then uses the product's
    list_price — same default Odoo uses).

    TODO (Phase 2): replace with ai.llm.complete_structured().
    """
    items = []
    seen = set()
    segments = re.split(r"[\n;,]|\band\b|\bwith\b", text, flags=re.IGNORECASE)
    for raw in segments:
        seg = raw.strip(" .-")
        if not seg:
            continue
        m = re.match(
            r"^(?:(?P<qty1>\d+(?:\.\d+)?)\s*[xX*×]?\s+)?"   # '3 x'  or '3 '
            r"(?P<name>[A-Za-z][A-Za-z0-9_\- ]*?)"            # product name
            r"(?:\s*@\s*(?P<price>\d+(?:\.\d+)?))?"           # '@ 1850'
            r"(?:\s*(?:per|/)\s*(?P<price2>[A-Za-z0-9_\- ]+))?"  # 'per LED Panel'
            r"(?:\s*[xX*×]\s*(?P<qty2>\d+(?:\.\d+)?))?$",     # 'LED Panel x 3'
            seg,
        )
        if not m:
            continue
        name = m.group("name").strip()
        if not name or name.lower() in _STOP:
            continue
        price = m.group("price")
        qty = m.group("qty1") or m.group("qty2") or "1"
        key = (name.lower(), qty, price)
        if key in seen:
            continue
        seen.add(key)
        # has_spec: the text actually stated a quantity or a price, so this is
        # clearly an order line — not a bare noun phrase ("hello how are you").
        has_spec = bool(m.group("qty1") or m.group("qty2") or price)
        items.append({
            "product_name": name,
            "quantity": float(qty),
            "price_unit": float(price) if price else None,
            "has_spec": has_spec,
        })
    return items
