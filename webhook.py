from flask import Flask, request
from database import save_message
from dotenv import load_dotenv
import os
import pandas as pd
from groq import Groq
from twilio.twiml.voice_response import VoiceResponse, Gather
import json


load_dotenv()

app = Flask(__name__)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
business_id = 1

def extract_intent(message_text):
    prompt = f"""Classify this WhatsApp reply from a customer about an overdue payment into exactly one category: Paid, Promise, Dispute, or Unclear.

Examples:
Message: "already paid yesterday" → Paid
Message: "will send by friday" → Promise
Message: "haan bhai kal kar dunga" → Promise
Message: "this amount seems wrong" → Dispute
Message: "who is this" → Unclear

Reply with ONLY valid JSON in this exact format: {{"intent": "..."}}

Message: "{message_text}" """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

@app.route("/whatsapp-reply", methods=["POST"])
def whatsapp_reply():
    incoming_message = request.form.get("Body")
    sender_number = request.form.get("From")
    clean_phone = sender_number.replace("whatsapp:", "").replace("+", "")

    category = extract_intent(incoming_message).get("intent")
    customer_name = get_customer_name(clean_phone)

    save_message(
        customer_name=customer_name,
        phone=clean_phone,
        direction="incoming",
        message_text=incoming_message,
        classification=category,
        business_id=business_id
    )

    print(f"From {customer_name} ({sender_number}): '{incoming_message}' → classified as: {category}")

    return "OK", 200





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


if __name__ == "__main__":
    app.run(port=5000)