import sqlite3

def get_connection():
    # Connects to (or creates, if it doesn't exist) the database file
    conn = sqlite3.connect("reminders.db")
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            direction TEXT,
            message_text TEXT,
            classification TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database and table ready.")



def save_message(customer_name, phone, direction, message_text, classification=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (customer_name, phone, direction, message_text, classification)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_name, phone, direction, message_text, classification))

    conn.commit()
    conn.close()

def get_history(phone):
    phone = phone.replace("+", "")  # normalize: strip + if present

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT direction, message_text, classification, timestamp
        FROM messages
        WHERE phone = ?
        ORDER BY timestamp ASC
    """, (phone,))

    rows = cursor.fetchall()
    conn.close()
    return rows
def get_all_messages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    history = get_history("+919417170517")
    print(f"Found {len(history)} messages")
    for row in history:
        print(row)