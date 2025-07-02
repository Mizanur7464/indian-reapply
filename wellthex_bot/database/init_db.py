import sqlite3

SCHEMA_PATH = "wellthex_bot/database/schema.sql"
DB_PATH = "wellthex_bot/airdrop.db"

def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    # Ensure 'instagram' column exists
    try:
        conn.execute('ALTER TABLE users ADD COLUMN instagram TEXT;')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    conn.close()
    print("Database initialized!")

if __name__ == "__main__":
    init_db() 