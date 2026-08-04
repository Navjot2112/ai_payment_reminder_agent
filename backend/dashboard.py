import csv
import pandas as pd
from datetime import date, datetime
from dotenv import load_dotenv
from database import get_all_messages
import os
from twilio.rest import Client
from make_call import initiate_call

load_dotenv()
business_id = 1 

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
owner_number = "whatsapp:+919417170517"  # YOUR number, to receive alerts

client = Client(account_sid, auth_token)

NGROK_URL = "https://oink-falcon-copartner.ngrok-free.dev"  # update each session


def get_all_messages_df():
    rows = get_all_messages(business_id=business_id)
    columns = ["id", "business_id", "customer_name", "phone", "direction",
               "message_text", "classification", "timestamp"]
    df = pd.DataFrame(rows, columns=columns)
    return df

    rename_map = {
        "customerName": "customer_name",
        "customer": "customer_name",
        "phone_number": "phone",
        "direction_type": "direction",
        "message": "message_text",
        "text": "message_text",
        "classification_status": "classification",
        "created_at": "timestamp",
        "sent_at": "timestamp",
    }
    df = df.rename(columns=rename_map)

    expected_columns = [
        "id",
        "business_id",
        "customer_name",
        "phone",
        "direction",
        "message_text",
        "classification",
        "timestamp",
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    return df[expected_columns]

def notify_owner(red_customers):
    if not red_customers:
        return

    names = ", ".join(red_customers)
    body = f"⚠️ Payment Reminder Alert: These customers need your attention: {names}"

    client.messages.create(
        from_=from_number,
        to=owner_number,
        body=body
    )
    print(f"Notification sent for: {names}")

def get_overdue_bills():
    today = date.today()
    overdue_bills = []

    with open("bills.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            due_date = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
            amount = float(row["amount"])

            if today > due_date:
                days_late = (today - due_date).days
                overdue_bills.append({
                    "customer": row["customer"],
                    "amount": amount,
                    "due_date": row["due_date"],
                    "days_late": days_late,
                })

    return overdue_bills


def get_dashboard_rows():
    messages = get_all_messages_df()
    if messages.empty:
        return []

    rows = []
    customers = messages["customer_name"].unique()

    for customer in customers:
        customer_msgs = messages[messages["customer_name"] == customer]
        outgoing = customer_msgs[customer_msgs["direction"] == "outgoing"]
        incoming = customer_msgs[customer_msgs["direction"] == "incoming"]

        sent_count = len(outgoing)
        reply_count = len(incoming)

        if reply_count > 0:
            latest_reply = incoming.sort_values("timestamp").iloc[-1]
            latest_status = latest_reply["classification"]
        else:
            latest_status = "No reply"

        if latest_status == "Paid":
            flag = "Green"
        elif latest_status == "Promise":
            flag = "Yellow"
        elif latest_status in ["Dispute", "Unclear"]:
            flag = "Red"
        elif latest_status == "No reply" and sent_count >= 2:
            flag = "Red"
        else:
            flag = "New"

        rows.append({
            "customer": customer,
            "sent": sent_count,
            "replies": reply_count,
            "latest_status": latest_status,
            "flag": flag,
        })

    return rows


def build_dashboard():
    rows = get_dashboard_rows()

    if not rows:
        print("No messages found yet.")
        return

    messages = get_all_messages_df()
    red_customers = []

    print(f"{'Customer':<20}{'Sent':<8}{'Replies':<10}{'Latest Status':<15}{'Flag'}")
    print("-" * 65)

    for row in rows:
        flag_label = {
            "Green": "🟢 Green",
            "Yellow": "🟡 Yellow",
            "Red": "🔴 Red",
            "New": "⚪ New",
        }[row["flag"]]

        if row["flag"] == "Red":
            red_customers.append(row["customer"])
            customer_msgs = messages[messages["customer_name"] == row["customer"]]
            if row["sent"] >= 2:
                customer_phone = "+" + customer_msgs.iloc[0]["phone"]
                initiate_call(
                    to_number=customer_phone,
                    webhook_url=NGROK_URL,
                    customer_name=row["customer"],
                    invoice_no="INV00X",
                    amount="15000",
                    days_late="10"
                )

        print(
            f"{row['customer']:<20}{row['sent']:<8}{row['replies']:<10}"
            f"{row['latest_status']:<15}{flag_label}"
        )

    notify_owner(red_customers)

if __name__ == "__main__":
    build_dashboard()
    