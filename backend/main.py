import csv
from datetime import date, datetime

def build_message(customer, amount, days_late):
    if days_late <= 7:
        opener = "just a friendly reminder that"
    elif days_late <= 15:
        opener = "this is a follow-up reminder that"
    else:
        opener = "this is an urgent reminder that"

    return (
        f"Hi {customer}, {opener} your payment of ₹{amount:,.2f} "
        f"is now {days_late} days overdue. Please arrange payment "
        f"at your earliest convenience. Thank you!"
    )


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
                "days_late": days_late
            })

print(f"Found {len(overdue_bills)} overdue bills:\n")
for bill in overdue_bills:
    message = build_message(bill["customer"], bill["amount"], bill["days_late"])
    print(message)
    print("---")