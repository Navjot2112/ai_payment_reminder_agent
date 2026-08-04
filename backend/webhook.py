from flask import Flask, request
from backend.database import save_message
from dotenv import load_dotenv
import os
import pandas as pd
from groq import Groq
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import json
from backend.database import save_message, save_invoice, get_invoices, update_invoice_status
from flask import Flask, request, jsonify
from backend.faq import search_faq
from flask_cors import CORS
import re
from backend.database import save_message, save_invoice, get_invoices, update_invoice_status, increment_reminder_count, save_pending_approval, get_pending_approvals, resolve_pending_approval
import base64
from backend.database import save_promise

from backend.make_call import initiate_call 

load_dotenv()
owner_number = "whatsapp:+919417170517"
app = Flask(__name__)
CORS(app)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
twilio_client = Client(account_sid, auth_token)
business_id = 1

faq_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": "Search Sahib Industries FAQ database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
@app.route("/api/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json()

    customer_name = data.get("customer")
    phone = re.sub(r'\D', '', data.get("phone") or "") or "0000000000"
    
    invoice_no = data.get("invoiceNo", "")
    amount = data.get("amount")
    due_date = data.get("dueDate")
    sender = data.get("sender")
    gst_amount = data.get("gstAmount")
    delivery_date = data.get("deliveryDate")
    payment_date = data.get("paymentDate")

    if not customer_name or not amount or not due_date:
        return jsonify({"message": "Missing required fields"}), 400

    invoice_id = save_invoice(
        business_id=business_id,
        customer_name=customer_name,
        phone=phone or "0000000000",  # placeholder if not provided
        invoice_no=invoice_no,
        amount=amount,
        due_date=due_date,
        sender=sender,
        gst_amount=gst_amount,
        delivery_date=delivery_date,
        payment_date=payment_date,
    )

    return jsonify({
        "id": invoice_id,
        "customer": customer_name,
        "invoiceNo": invoice_no,
        "amount": amount,
        "dueDate": due_date,
        "phone": phone,
        "sender": sender,
        "gstAmount": gst_amount,
        "deliveryDate": delivery_date,
        "paymentDate": payment_date,
        "status": "overdue" if due_date < __import__("datetime").date.today().isoformat() else "upcoming",
        "reminders": 0,
    }), 201

@app.route("/api/invoices", methods=["GET"])
def list_invoices():
    from datetime import date as _date
    invoices = get_invoices(business_id=business_id)
    result = []
    for inv in invoices:
        status = "overdue" if inv["due_date"] < _date.today().isoformat() and inv["status"] != "paid" else (inv["status"] if inv["status"] == "paid" else "upcoming")
        result.append({
            "id": inv["id"],
            "customer": inv["customer_name"],
            "invoiceNo": inv["invoice_no"],
            "amount": inv["amount"],
            "dueDate": inv["due_date"],
            "phone": inv["phone"],
            "status": status,
            "reminders": inv["reminder_count"],
        })
    return jsonify(result), 200

@app.route("/api/invoices/<int:invoice_id>/history", methods=["GET"])
def invoice_history(invoice_id):
    from backend.database import get_history
    invoices = get_invoices(business_id=business_id)
    invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
    if not invoice:
        return jsonify({"message": "Invoice not found"}), 404

    try:
        history = get_history(business_id=business_id, phone=invoice["phone"])
    except Exception as e:
        print(f"Failed to fetch history: {e}")
        return jsonify({"message": "Could not fetch history"}), 500

    return jsonify([
        {
            "direction": h[0],
            "message": h[1],
            "classification": h[2],
            "timestamp": h[3].isoformat()
        }
        for h in history
    ]), 200


@app.route("/api/invoices/<int:invoice_id>/receipt", methods=["POST"])
def upload_receipt(invoice_id):
    # Expecting a file upload in request.files with key 'receipt'
    if 'receipt' not in request.files:
        return jsonify({"message": "No file part 'receipt' in the request"}), 400

    file = request.files['receipt']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    try:
        # Optionally save the file; create receipts/ if needed
        import os
        receipts_dir = os.path.join(os.getcwd(), 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)
        filepath = os.path.join(receipts_dir, f"invoice_{invoice_id}_" + file.filename)
        file.save(filepath)

        # Update invoice status to paid
        update_invoice_status(invoice_id, "paid")
    except Exception as e:
        print(f"Failed to process receipt upload: {e}")
        return jsonify({"message": "Failed to upload receipt"}), 500

    return jsonify({"message": "Receipt uploaded and invoice marked paid"}), 200



def extract_intent(message_text):
    prompt = f"""Classify this WhatsApp reply from a customer about an overdue payment into exactly one category: Paid, Promise, Dispute, Question, or Unclear.

Examples:
Message: "already paid yesterday" → Paid
Message: "will send by friday" → Promise
Message: "haan bhai kal kar dunga" → Promise
Message: "this amount seems wrong" → Dispute
Message: "who is this" → Question
Message: "what payment methods do you accept" → Question
Message: "when will my order arrive" → Question
Message: "hmm ok" → Unclear
Message: "I have a question about my invoice" → Question
Message: "I don't recognize this charge" → Dispute
Message: "I have already paid this invoice" → Paid
Message: "meri payment ho gayi hai" → Paid
Reply with ONLY valid JSON in this exact format: {{"intent": "...", "promised_date": null, "sender": null, "gst_amount": null, "delivery_date": null, "payment_date": null}}
If the intent is Promise, set "promised_date" to the promised payment date in YYYY-MM-DD format if the message contains a clear promise date, otherwise null.
Include any invoice-related fields mentioned in the message (sender company, GST amount, delivery date, payment date) or null if not mentioned.
Message: "{message_text}" """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def get_customer_name(phone):
    bills = pd.read_csv("bills.csv" , dtype={"phone": str})
    bills["phone_clean"] = bills["phone"].astype(str).str.replace("+", "", regex=False)
    match = bills[bills["phone_clean"] == phone]
    if len(match) > 0:
        return match.iloc[0]["customer_name"]
    else:
        return "Unknown"


def get_reply_message(category):
    replies = {
        "Paid": "Thanks for confirming the payment. We'll mark this invoice as paid.",
        "Promise": "Thank you for the update. We'll follow up if needed.",
        "Dispute": "We received your concern and will review the invoice details.",
        "Unclear": "Thanks for your message. Can you please clarify your payment status?",
        "Question": "Thanks for reaching out. We'll get back to you with the information you requested."
    }
    return replies.get(category, "Thanks for your message. We'll get back to you soon.")

@app.route("/api/invoices/extract", methods=["POST"])
def extract_invoice_from_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    mime_type = image_file.mimetype or "image/jpeg"
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = """This is a tax invoice. Extract the following fields and return ONLY valid JSON:

{
  "customer": "the BUYER's name (look for 'Bill to', 'Buyer', or similar — NOT the seller/company issuing the invoice)",
  "invoiceNo": "the invoice number (look for 'Invoice No.' specifically)",
  "amount": "the FINAL TOTAL amount to be paid, as a plain number with no currency symbol or commas (usually the grand total at the bottom, not a line-item subtotal)",
  "dueDate": "the invoice date in YYYY-MM-DD format (look for 'Dated' near the invoice number; if no separate due date exists, use the invoice date)",
  "phone": "the BUYER's phone number if visible, else null (do NOT use the seller's contact number)",
  "sender": "the SELLER's company name or address (the party issuing the invoice, usually at the top with logo)",
  "gstAmount": "the GST amount as a number with no currency symbol, else null",
  "deliveryDate": "the delivery/supply date in YYYY-MM-DD format if visible, else null",
  "paymentDate": "the payment due date in YYYY-MM-DD format if different from invoice date, else null"
}

Be careful to distinguish the SELLER (the company issuing the invoice, usually at the top with a logo) from the BUYER (the customer being billed, usually under 'Bill to' or 'Buyer').
"""

    try:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}}
            ]}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response.choices[0].message.content)
        return jsonify(extracted), 200
    except Exception as e:
        print(f"Extraction failed: {e}")
        return jsonify({"message": "Could not read this image. Please enter details manually."}), 422


@app.route("/whatsapp-reply", methods=["POST"])
def whatsapp_reply():
    incoming_message = request.form.get("Body")
    sender_number = request.form.get("From")
    clean_phone = sender_number.replace("whatsapp:", "").replace("+", "")

    customer_name = get_customer_name(clean_phone)
    extracted = extract_intent(incoming_message)
    category = extracted.get("intent")
    promised_date = extracted.get("promised_date")
    customer_name = get_customer_name(clean_phone)

    if category == "Question":
        faq_answer = search_faq(incoming_message)
        if faq_answer:
            reply_text = faq_answer
        else:
            reply_text = "Thanks for your question — we'll get back to you shortly."
            save_pending_approval(business_id, customer_name, clean_phone, incoming_message)
            twilio_client.messages.create(
                from_=from_number,
                to=owner_number,
                body=f"❓ {customer_name} asked something the FAQ couldn't answer: \"{incoming_message}\""
            )
    elif category == "Promise" and promised_date:
        save_promise(business_id, customer_name, clean_phone, promised_date)
        reply_text = get_reply_message(category)
    else:
        reply_text = get_reply_message(category)

    save_message(
        customer_name=customer_name,
        phone=clean_phone,
        direction="incoming",
        message_text=incoming_message,
        classification=category,
        business_id=business_id
    )

    twilio_client.messages.create(
        body=reply_text,
        from_=from_number,
        to=sender_number
    )

    save_message(
        customer_name=customer_name,
        phone=clean_phone,
        direction="outgoing",
        message_text=reply_text,
        business_id=business_id
    )

    print(f"From {customer_name} ({sender_number}): '{incoming_message}' → classified as: {category} | reply: {reply_text}")

    return "OK", 200


@app.route("/api/promises", methods=["GET"])
def list_promises():
    from backend.database import get_promises
    return jsonify(get_promises(business_id=business_id)), 200

@app.route("/api/invoices/<int:invoice_id>/remind", methods=["POST"])
def remind_invoice(invoice_id):
    invoices = get_invoices(business_id=business_id)
    invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
    if not invoice:
        return jsonify({"message": "Invoice not found"}), 404

    reminder_text = f"Hi {invoice['customer_name']}, this is a reminder that invoice {invoice['invoice_no']} for ₹{invoice['amount']} is due on {invoice['due_date']}. Please arrange payment."

    clean_number = re.sub(r'\D', '', invoice['phone'])

    try:
        twilio_client.messages.create(
            body=reminder_text,
            from_=from_number,
            to=f"whatsapp:+{clean_number}"
        )
    except Exception as e:
        print(f"Failed to send reminder: {e}")
        return jsonify({"message": f"Could not send reminder: invalid or unreachable phone number ({invoice['phone']})"}), 422

    save_message(
        business_id=business_id,
        customer_name=invoice["customer_name"],
        phone=clean_number,
        direction="outgoing",
        message_text=reminder_text,
    )

    new_count = increment_reminder_count(invoice_id)

    return jsonify({
        "id": invoice["id"],
        "customer": invoice["customer_name"],
        "invoiceNo": invoice["invoice_no"],
        "amount": invoice["amount"],
        "dueDate": invoice["due_date"],
        "phone": invoice["phone"],
        "status": invoice["status"],
        "reminders": new_count,
    }), 200


@app.route("/api/analytics/revenue", methods=["GET"])
def revenue_analytics():
    from datetime import date as _date
    invoices = get_invoices(business_id=business_id)
    today = _date.today()

    collected_this_month = sum(
        inv["amount"] for inv in invoices
        if inv["status"] == "paid" and inv["due_date"][:7] == today.isoformat()[:7]
    )
    expected_this_month = sum(
        inv["amount"] for inv in invoices
        if inv["status"] != "paid" and inv["due_date"][:7] == today.isoformat()[:7]
    )
    overdue_total = sum(
        inv["amount"] for inv in invoices
        if inv["status"] != "paid" and inv["due_date"] < today.isoformat()
    )

    return jsonify({
        "collectedThisMonth": collected_this_month,
        "expectedThisMonth": expected_this_month,
        "overdueTotal": overdue_total,
    }), 200


@app.route("/voice-handle", methods=["POST"])
def voice_handle():
    speech_text = request.form.get("SpeechResult", "")
    intent = extract_intent(speech_text)

    resp = VoiceResponse()
    if intent["intent"] == "Paid":
        resp.say("Great, thank you! Goodbye.", voice="Polly.Aditi")
    else:
        resp.say("Understood, we'll follow up. Goodbye.", voice="Polly.Aditi")
    return str(resp)

@app.route("/voice-start", methods=["POST"])
def voice_start():
    name = request.args.get("name", "customer")
    invoice = request.args.get("invoice", "your invoice")
    amount = request.args.get("amount", "the amount")
    days = request.args.get("days", "some")

    resp = VoiceResponse()
    gather = Gather(input="speech", action="/voice-handle", timeout=5)
    gather.say(
        f"Hi {name}, this is regarding invoice {invoice} for {amount} rupees, "
        f"which is {days} days overdue. Have you made the payment?",
        voice="Polly.Aditi"
    )
    resp.append(gather)
    return str(resp)




def answer_question(user_message):

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ],
        tools=faq_tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if not message.tool_calls:
        return None

    tool_call = message.tool_calls[0]

    args = json.loads(tool_call.function.arguments)

    faq_answer = search_faq(args["query"])

    return faq_answer


NGROK_URL = "https://oink-falcon-copartner.ngrok-free.dev"  # update each session, same as dashboard.py

@app.route("/api/invoices/<int:invoice_id>/call", methods=["POST"])
def call_invoice(invoice_id):
    invoices = get_invoices(business_id=business_id)
    invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
    if not invoice:
        return jsonify({"message": "Invoice not found"}), 404

    clean_number = re.sub(r'\D', '', invoice['phone'])

    from datetime import date as _date
    days_late = (_date.today() - _date.fromisoformat(invoice['due_date'])).days
    days_late = max(days_late, 0)

    try:
        initiate_call(
            to_number=f"+{clean_number}",
            webhook_url=NGROK_URL,
            customer_name=invoice['customer_name'],
            invoice_no=invoice['invoice_no'],
            amount=invoice['amount'],
            days_late=days_late,
        )
    except Exception as e:
        print(f"Failed to initiate call: {e}")
        return jsonify({"message": f"Could not place call: invalid or unreachable number ({invoice['phone']})"}), 422

    return jsonify({"message": f"Call initiated to {invoice['customer_name']}"}), 200

@app.route("/api/pending-questions", methods=["GET"])
def list_pending_questions():
    return jsonify(get_pending_approvals(business_id=business_id)), 200


@app.route("/api/pending-questions/<int:approval_id>/resolve", methods=["POST"])
def resolve_question(approval_id):
    data = request.get_json()
    owner_response = data.get("response")
    if not owner_response:
        return jsonify({"message": "Response text required"}), 400

    result = resolve_pending_approval(approval_id, owner_response)
    if not result:
        return jsonify({"message": "Not found"}), 404

    try:
        twilio_client.messages.create(
            body=owner_response,
            from_=from_number,
            to=f"whatsapp:+{result['phone']}"
        )
    except Exception as e:
        print(f"Failed to send owner response: {e}")
        return jsonify({"message": "Marked resolved but failed to send WhatsApp reply"}), 422

    return jsonify({"message": "Response sent to customer"}), 200

if __name__ == "__main__":
    app.run(port=5000)

