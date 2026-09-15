import sqlite3
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_id INTEGER,
            broker_name TEXT,
            client_name TEXT,
            client_phone TEXT,
            rep_number TEXT,
            proof_type TEXT,
            proof_content TEXT,
            status TEXT DEFAULT 'pending_number',
            created_at TEXT,
            number_added_at TEXT,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user(user_id, username, first_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def add_client(broker_id, broker_name, client_name, client_phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clients (broker_id, broker_name, client_name, client_phone, status, created_at)
        VALUES (?, ?, ?, ?, 'pending_number', ?)
    """, (broker_id, broker_name, client_name, client_phone, datetime.now().isoformat()))
    conn.commit()
    client_id = cur.lastrowid
    conn.close()
    return client_id


def get_client(client_id, broker_id=None):
    conn = get_conn()
    cur = conn.cursor()
    if broker_id:
        cur.execute("SELECT * FROM clients WHERE id=? AND broker_id=?", (client_id, broker_id))
    else:
        cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row


def add_rep_number(client_id, broker_id, rep_number):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clients SET rep_number=?, status='number_sent', number_added_at=?
        WHERE id=? AND broker_id=?
    """, (rep_number, datetime.now().isoformat(), client_id, broker_id))
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0


def add_proof(client_id, broker_id, proof_type, proof_content):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clients SET proof_type=?, proof_content=?, status='completed', completed_at=?
        WHERE id=? AND broker_id=?
    """, (proof_type, proof_content, datetime.now().isoformat(), client_id, broker_id))
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0


def get_pending_clients(broker_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM clients WHERE broker_id=? AND status != 'completed'
        ORDER BY created_at DESC
    """, (broker_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_user_stats(broker_id):
    conn = get_conn()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT COUNT(*) as cnt FROM clients
        WHERE broker_id=? AND status='completed' AND completed_at LIKE ?
    """, (broker_id, f"{today}%"))
    today_count = cur.fetchone()["cnt"]
    cur.execute("""
        SELECT COUNT(*) as cnt FROM clients WHERE broker_id=? AND status='completed'
    """, (broker_id,))
    total_count = cur.fetchone()["cnt"]
    conn.close()
    return today_count, total_count


def get_team_stats():
    conn = get_conn()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT broker_id, broker_name,
        SUM(CASE WHEN status='completed' AND completed_at LIKE ? THEN 1 ELSE 0 END) as today_cnt,
        SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as total_cnt
        FROM clients
        GROUP BY broker_id
        ORDER BY today_cnt DESC
    """, (f"{today}%",))
    rows = cur.fetchall()
    conn.close()
    return rows
def reset_all_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients")
    cursor.execute("DELETE FROM proofs")
    conn.commit()
    conn.close()
