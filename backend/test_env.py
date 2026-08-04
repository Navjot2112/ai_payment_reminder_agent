from dotenv import load_dotenv
import os

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")

print("SID:", sid)
print("Token starts:", token[:4] if token else None)
print("Token ends:", token[-4:] if token else None)
print("Token length:", len(token) if token else 0)