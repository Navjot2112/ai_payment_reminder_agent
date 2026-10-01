# Sales Pipeline Backend (Odoo core logic in plain Python/Flask)

A Python port of Odoo's core **product → quotation → invoice → payment** flow.
Same model names, same states, same "button" actions as Odoo — but a tiny
standalone Flask + SQLite app with **zero Odoo runtime dependency**.

This is **backend logic only** — pure JSON API. It does not touch or change
your UI; your frontend just calls these endpoints.

## Run it

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000
```

Seed data loads automatically on first start (taxes, one customer, 3 products).
`GET /api/health` to check it's alive.

## The exact plan — how the flow works

```
┌─────────────┐   ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐   ┌──────────────┐
│ 1. PRODUCTS │ -> │ 2. CUSTOMER │ -> │ 3. QUOTATION     │ -> │ 4. INVOICE          │ -> │ 5. PAYMENT   │
│ product     │    │ res.partner │    │ sale.order       │    │ account.move        │    │ account.     │
│ .product    │    │             │    │ draft->sent->sale│    │ out_invoice          │    │ payment      │
└─────────────┘    └─────────────┘    │  (QUOT/0001)     │    │ draft->posted->paid │    └──────────────┘
                                      └──────────────────┘    └─────────────────────┘
```

1. **Products** carry `list_price` (sale price), `standard_price` (cost) and default
   `tax_ids`. Prices and taxes on a quotation line default from the product —
   exactly like Odoo.
2. **Customer** is a `res.partner`.
3. **Quotation** is a `sale.order`. Creating one auto-numbers it `QUOT/0001`
   (ported `ir.sequence`). Lines can be edited **while draft**.
4. **Confirm** (`state: sale`) is the gate — after that the order is locked and
   you can **Create Invoice**: one `account.move` (type `out_invoice`) is built
   with one line per SO line, discount folded into unit price, taxes copied,
   `ref` = the QUOT number.
5. **Post** the invoice (`posted` = validated), then **register payment** →
   `paid` (or `partial` for partial payments). The SO's `invoice_status`
   (`no / partially_invoiced / invoiced / over_invoiced`) updates automatically.

### State machines (identical to Odoo)

| Document | States |
|---|---|
| sale.order | `draft → sent → sale → done`, `draft/sent → cancel` |
| account.move | `draft → posted → paid`, `posted → partial`, `draft → cancel` |

## Odoo → this project mapping

| Odoo model | File here | Notes |
|---|---|---|
| `product.product` / `product.template` | `models/product.py` | merged into one table, Odoo field names kept |
| `res.partner` | `models/partner.py` | |
| `account.tax` | `models/tax.py` | `tax_base` = total_excluded / total_included |
| `ir.sequence` | `models/sequence.py` | `next_by_id()` ported |
| `sale.order` / `sale.order.line` | `models/sale.py` | states + `action_confirm` etc. |
| `account.move` / `account.move.line` | `models/account_move.py` | |
| `account.payment` | `models/payment.py` | |
| tax computation | `services/tax.py` | |
| `sale.order.create_invoice()` | `services/invoice_service.py` | |
| ORM registry `env['model']` | `database.py` (SQLAlchemy) | |
| `UserError` | `common.py` | → HTTP 400 |

## Full end-to-end flow (copy-paste test)

```bash
# 0. see what's seeded
curl -s localhost:5000/api/products

# 1. customer (or use seeded partner id 1)
curl -s -X POST localhost:5000/api/partners \
  -H 'Content-Type: application/json' \
  -d '{"name":"Shivani Traders","email":"acc@shivani.com","city":"Pune"}'

# 2. create a QUOTATION  (price_unit/tax_ids optional -> defaults from product)
curl -s -X POST localhost:5000/api/sales \
  -H 'Content-Type: application/json' \
  -d '{"partner_id":1,"notes":"July order","lines":[
        {"product_id":1,"qty":2,"discount":10},
        {"product_id":2,"qty":5},
        {"product_id":3,"qty":2}
      ]}'
# -> {"name":"QUOT/0001","state":"draft","subtotal":15250.0,"tax_total":3281.5,...}

# 3. send + confirm
curl -s -X POST localhost:5000/api/sales/1/send
curl -s -X POST localhost:5000/api/sales/1/confirm

# 4. create the INVOICE from the confirmed order
curl -s -X POST localhost:5000/api/sales/1/create-invoice
# -> {"name":"INV/0001","ref":"QUOT/0001","state":"draft",...}

# 5. validate (post) the invoice
curl -s -X POST localhost:5000/api/invoices/1/post

# 6. register the payment
curl -s -X POST localhost:5000/api/invoices/1/payment \
  -H 'Content-Type: application/json' \
  -d '{"payment_method":"upi","communication":"UPI ref 12345"}'
# -> invoice.state = "paid"

# 7. verify the SO shows invoice_status: "invoiced"
curl -s localhost:5000/api/sales/1
```

## API reference

| Method | Endpoint | What it does (Odoo button) |
|---|---|---|
| GET/POST | `/api/products` | product list / create |
| GET/PUT/DELETE | `/api/products/<id>` | fetch / edit / **archive** (Odoo-style) |
| GET/POST | `/api/partners` | customer list / create |
| GET/PUT | `/api/partners/<id>` | fetch / edit |
| GET/POST | `/api/sales` | quotation list / **New Quotation** |
| GET/PUT | `/api/sales/<id>` | fetch / edit draft |
| POST | `/api/sales/<id>/send` | *Mark as Sent* |
| POST | `/api/sales/<id>/confirm` | **Confirm** |
| POST | `/api/sales/<id>/cancel` | *Cancel* |
| POST | `/api/sales/<id>/create-invoice` | **Create Invoice** |
| GET | `/api/invoices`, `/api/invoices/<id>` | invoice list / fetch |
| POST | `/api/invoices/<id>/post` | **Validate** |
| POST | `/api/invoices/<id>/payment` | **Register Payment** (body: `amount?`, `payment_method?`, `communication?`) |
| POST | `/api/invoices/<id>/cancel` | *Cancel* |
| POST | `/api/ai/draft-quotation` | 🤖 AI drafts a quotation from free text |
| GET | `/api/ai/health` | AI status |

Errors: business-rule violations → HTTP 400 `{"error": "..."}`; missing records → 404.

## 🤖 Future AI implementation roadmap (industry-grade)

The AI layer already exists as a working skeleton (`ai/` + `/api/ai/*`):
today `POST /api/ai/draft-quotation` parses "3 x LED Panel @ 1850 and 20 fans"
into a **real numbered draft quotation**, auto-creating missing products, and
returns `agent_steps` — a trace of every tool call. Swap the rule-based brain
for a real LLM in `ai/llm.py` and the whole pipeline keeps working unchanged.

**Phase 1 — Generative AI (weeks 1–2, demo-ready)**
- Wire `ai/llm.py` to OpenAI/Gemini/Ollama (`pip install openai`, set `LLM_API_KEY`).
- LLM structured output replaces the regex extractor (better names, quantities, prices, discounts).
- Generate product descriptions / quotation letters / email summaries.

**Phase 2 — Agentic AI (weeks 3–6, the "wow" layer)**
- Real **tool-calling agent**: give the LLM tools = `product.lookup`,
  `product.create`, `quotation.draft`, `quotation.confirm`, `invoice.create`,
  `payment.register`. User says *"quote Acme 20 fans and invoice them"* →
  the agent plans and executes the steps, showing `agent_steps` in the UI.
- Guardrails: agent can *draft* only — **confirm/invoice/payment stay behind
  human approval** (this is exactly how enterprise AI agents are designed).
- Voice / WhatsApp / chat entry: same tools, different input channel.

**Phase 3 — Industry intelligence (months 2–4, where the value is)**
- **Predictive pricing**: suggest `price_unit` from history (season, customer
  tier, discount patterns) — start with a simple regression, add an LLM explainer.
- **Demand forecasting** per product/customer → purchase & stock suggestions.
- **Invoice automation**: OCR a photo of a supplier bill (gen-AI vision) →
  draft vendor invoice; anomaly detection (duplicate invoice, price drift > x%).
- **Collections agent**: NLP on email thread + payment history →
  "this customer pays late, send reminder 5 days before due" (fits your
  reminder-agent project perfectly).
- **Document generation**: LLM writes the quotation PDF letter, the follow-up,
  the credit note.
- **RAG knowledge base**: company price list, contract terms, past orders —
  agent answers "what did we charge Acme last year?" with citations.

**Phase 4 — Production hardening**
- Auth (JWT), role-based access (salesperson vs accountant), audit log of
  every human *and* AI action, Postgres switch (`DATABASE_URL` env var),
  tests, Docker.

The architecture point to show in interviews/demos: **the AI never touches
the database directly — it emits structured tool calls, and the same
Odoo-style business logic executes them.** That's what makes it safe to ship
to real companies.
