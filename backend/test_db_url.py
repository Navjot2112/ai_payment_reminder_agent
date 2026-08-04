from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("DB URL loaded:", db_url[:25] + "..." if db_url else "NOT FOUND")