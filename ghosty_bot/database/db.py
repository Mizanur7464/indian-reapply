import sqlite3

def get_db_connection():
    conn = sqlite3.connect('ghosty_bot/airdrop.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_user(user_id, username, status, referrer_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''INSERT OR IGNORE INTO users (user_id, username, status, referrer_id) VALUES (?, ?, ?, ?)''',
                (user_id, username, status, referrer_id))
    conn.commit()
    conn.close()

def set_email_verified(user_id, email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''UPDATE users SET email = ?, email_verified = 1 WHERE user_id = ?''', (email, user_id))
    conn.commit()
    conn.close()

def init_user_tasks(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''INSERT OR IGNORE INTO user_tasks (user_id) VALUES (?)''', (user_id,))
    conn.commit()
    conn.close()

def set_task_completed(user_id, task):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'''UPDATE user_tasks SET {task} = 1 WHERE user_id = ?''', (user_id,))
    conn.commit()
    conn.close()

def get_next_incomplete_task(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT twitter, instagram, telegram, telegram_channel, youtube FROM user_tasks WHERE user_id = ?''', (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return 'twitter'
    for task in ['twitter', 'instagram', 'telegram', 'telegram_channel', 'youtube']:
        if row[task] == 0:
            return task
    return None

def set_referrer(user_id, referrer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''UPDATE users SET referrer_id = ? WHERE user_id = ?''', (referrer_id, user_id))
    conn.commit()
    conn.close()

def add_wtx(user_id, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''UPDATE users SET wtx = COALESCE(wtx, 0) + ? WHERE user_id = ?''', (amount, user_id))
    conn.commit()
    conn.close()

def get_referrer_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT referrer_id FROM users WHERE user_id = ?''', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row['referrer_id']
    return None

def set_wallet(user_id, wallet):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''UPDATE users SET wallet = ? WHERE user_id = ?''', (wallet, user_id))
    conn.commit()
    conn.close()

def get_user_status(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT email_verified, wallet FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'email_verified': row['email_verified'], 'wallet': row['wallet']}
    return None

def get_user_tasks(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT twitter, instagram, telegram, telegram_channel, youtube FROM user_tasks WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'twitter': row['twitter'],
            'instagram': row['instagram'],
            'telegram': row['telegram'],
            'telegram_channel': row['telegram_channel'],
            'youtube': row['youtube']
        }
    return None

def get_user_info(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT email, wallet, wtx, username, instagram FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'email': row['email'],
            'wallet': row['wallet'],
            'wtx': row['wtx'],
            'username': row['username'],
            'instagram': row['instagram']
        }
    return None

def get_referral_count(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users WHERE referrer_id = ?', (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def set_twitter_username(user_id, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET username = ? WHERE user_id = ?', (username, user_id))
    conn.commit()
    conn.close()

def set_instagram_username(user_id, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET instagram = ? WHERE user_id = ?', (username, user_id))
    conn.commit()
    conn.close()

def get_airdrop_claimed(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT airdrop_claimed FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row['airdrop_claimed']
    return 0

def set_airdrop_claimed(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET airdrop_claimed = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close() 