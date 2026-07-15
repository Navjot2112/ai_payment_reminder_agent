from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from twilio.rest import Client
from database import save_message

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)

MILD_THRESHOLD = 7
FIRM_THRESHOLD = 15

def calculate_days_late(row):
    return (datetime.now() - row["due_date"]).days

def get_status(days_late):
    if days_late <= 0:
        return "Not Due"
    elif days_late <= MILD_THRESHOLD:
        return "Mild"
    elif days_late <= FIRM_THRESHOLD:
        return "Firm"
    else:
        return "Urgent"

def build_message(row):
    name = row["customer_name"]
    invoice = row["invoice_no"]
    days = row["days_late"]
    status = row["status"]

    if status == "Mild":
        return f"Hi {name}, just a friendly reminder that invoice {invoice} is {days} day(s) overdue. Please arrange payment at your convenience. Thank you!"
    elif status == "Firm":
        return f"Hi {name}, invoice {invoice} is now {days} days overdue. Kindly clear this payment soon to avoid further delays. Please let us know if there's an issue."
    elif status == "Urgent":
        return f"Hi {name}, invoice {invoice} is significantly overdue by {days} days. Immediate payment is required. Please contact us urgently to resolve this."
    else:
        return None

bills = pd.read_csv("bills.csv")
bills["due_date"] = pd.to_datetime(bills["due_date"])
bills["days_late"] = bills.apply(calculate_days_late, axis=1)
bills["status"] = bills["days_late"].apply(get_status)

for index, row in bills.iterrows():
    if row["status"] == "Not Due":
        print(f"Skipping {row['customer_name']} — not due yet")
        continue

    message_text = build_message(row)
    to_number = f"whatsapp:{row['phone']}"

    message = client.messages.create(
        from_=from_number,
        to=to_number,
        body=message_text
    )

    save_message(
        customer_name=row["customer_name"],
        phone=row["phone"],
        direction="outgoing",
        message_text=message_text
    )

    print(f"Sent to {row['customer_name']} ({row['status']}) — SID: {message.sid}")