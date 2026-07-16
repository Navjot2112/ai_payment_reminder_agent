from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv()
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

messages = client.messages.list(limit=5)
for msg in messages:
    print(f"SID: {msg.sid} | To: {msg.to} | Status: {msg.status} | Error: {msg.error_code} - {msg.error_message}")