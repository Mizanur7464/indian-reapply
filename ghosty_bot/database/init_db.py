import sqlite3
import os

SCHEMA_PATH = "database/schema.sql"
DB_PATH = "airdrop.db"

def ensure_telegram_channel_column():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check if telegram_channel column exists
    cur.execute("PRAGMA table_info(user_tasks);")
    columns = [row[1] for row in cur.fetchall()]
    if 'telegram_channel' not in columns:
        try:
            cur.execute("ALTER TABLE user_tasks ADD COLUMN telegram_channel INTEGER DEFAULT 0;")
            print("telegram_channel column added to user_tasks table.")
        except Exception as e:
            print("Error adding telegram_channel column:", e)
    conn.commit()
    conn.close()

def ensure_airdrop_claimed_column():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users);")
    columns = [row[1] for row in cur.fetchall()]
    if 'airdrop_claimed' not in columns:
        try:
            cur.execute("ALTER TABLE users ADD COLUMN airdrop_claimed INTEGER DEFAULT 0;")
            print("airdrop_claimed column added to users table.")
        except Exception as e:
            print("Error adding airdrop_claimed column:", e)
    conn.commit()
    conn.close()

def init_db():
    # Always create/update database
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
    conn.commit()
    conn.close()
    print("Database initialized!")
    ensure_telegram_channel_column()
    ensure_airdrop_claimed_column()

if __name__ == "__main__":
    init_db() 