from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Classify this message as one of: Paid, Promise, Dispute, Unclear. Reply with only that one word. Message: haan bhai kal kar dunga"}
    ]
)

print(response.choices[0].message.content)