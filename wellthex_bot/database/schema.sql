CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    status TEXT,
    email TEXT,
    email_verified INTEGER DEFAULT 0,
    referrer_id INTEGER,
    wtx INTEGER DEFAULT 0,
    wallet TEXT,
    airdrop_claimed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_tasks (
    user_id INTEGER PRIMARY KEY,
    twitter INTEGER DEFAULT 0,
    instagram INTEGER DEFAULT 0,
    telegram INTEGER DEFAULT 0,
    telegram_channel INTEGER DEFAULT 0,
    youtube INTEGER DEFAULT 0
); 