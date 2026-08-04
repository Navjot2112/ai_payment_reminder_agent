from dotenv import load_dotenv
import os
import json
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FAQS = {
    "who are you":
        "Sahib Industries is a manufacturer and supplier of industrial products based in Punjab.",

    "payment methods":
        "We accept UPI, NEFT/RTGS bank transfer, cheque and cash.",

    "delivery":
        "Orders are generally dispatched within 2–5 working days.",

    "gst":
        "Yes. We provide GST invoices with every order.",

    "contact":
        "You can contact us at +91 94171 70517.",

    "business hours":
        "Monday to Saturday, 9 AM to 6 PM.",

    "minimum order":
        "Minimum order depends on the product category.",

    "location":
        "We are located in Punjab, India."
}


def search_faq(query):
    faq_list = "\n".join([f"- {k}: {v}" for k, v in FAQS.items()])
    prompt = f"""Given this customer question, pick the BEST matching FAQ topic key from this list, or return "no_match" if nothing fits well.

FAQ topics:
{faq_list}

Customer question: "{query}"

Reply with ONLY valid JSON: {{"key": "..."}}"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    matched_key = result.get("key")
    return FAQS.get(matched_key)