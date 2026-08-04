from dotenv import load_dotenv
import os
import urllib.parse
from twilio.rest import Client

load_dotenv()
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

def initiate_call(to_number, webhook_url, customer_name, invoice_no, amount, days_late):
    params = urllib.parse.urlencode({
        "name": customer_name,
        "invoice": invoice_no,
        "amount": amount,
        "days": days_late
    })
    call = client.calls.create(
        to=to_number,
        from_=os.getenv("TWILIO_VOICE_NUMBER"),
        url=f"{webhook_url}/voice-start?{params}"
    )
    print("Call started:", call.sid)