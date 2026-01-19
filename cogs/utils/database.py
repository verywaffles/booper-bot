import sqlite3
from pathlib import Path

# -----------------------------
# Database Path
# -----------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "economy.db"


# -----------------------------
# Connection Helper
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Initialize Tables
# -----------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            wallet INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            job TEXT,
            job_level INTEGER DEFAULT 1,
            last_daily INTEGER,
            last_weekly INTEGER
        )
    """)

    # Inventory table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item TEXT,
            amount INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, item)
        )
    """)

    # Cooldowns table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id INTEGER,
            command TEXT,
            last_used INTEGER,
            PRIMARY KEY (user_id, command)
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# User Helpers
# -----------------------------
def ensure_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO users (user_id, wallet, bank) VALUES (?, 0, 0)",
            (user_id,)
        )
        conn.commit()

    conn.close()


def get_balance(user_id: int):
    ensure_user(user_id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT wallet, bank FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row["wallet"], row["bank"]


def set_balance(user_id: int, wallet: int, bank: int):
    ensure_user(user_id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET wallet = ?, bank = ? WHERE user_id = ?",
        (wallet, bank, user_id)
    )

    conn.commit()
    conn.close()


def change_wallet(user_id: int, amount: int):
    wallet, bank = get_balance(user_id)
    wallet += amount
    if wallet < 0:
        wallet = 0
    set_balance(user_id, wallet, bank)


def change_bank(user_id: int, amount: int):
    wallet, bank = get_balance(user_id)
    bank += amount
    if bank < 0:
        bank = 0
    set_balance(user_id, wallet, bank)


# -----------------------------
# Inventory Helpers
# -----------------------------
def add_item(user_id: int, item: str, amount: int = 1):
    ensure_user(user_id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT amount FROM inventory WHERE user_id = ? AND item = ?",
        (user_id, item)
    )
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO inventory (user_id, item, amount) VALUES (?, ?, ?)",
            (user_id, item, amount)
        )
    else:
        new_amount = row["amount"] + amount
        cur.execute(
            "UPDATE inventory SET amount = ? WHERE user_id = ? AND item = ?",
            (new_amount, user_id, item)
        )

    conn.commit()
    conn.close()


def remove_item(user_id: int, item: str, amount: int = 1):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT amount FROM inventory WHERE user_id = ? AND item = ?",
        (user_id, item)
    )
    row = cur.fetchone()

    if row is None:
        conn.close()
        return False

    new_amount = row["amount"] - amount
    if new_amount <= 0:
        cur.execute(
            "DELETE FROM inventory WHERE user_id = ? AND item = ?",
            (user_id, item)
        )
    else:
        cur.execute(
            "UPDATE inventory SET amount = ? WHERE user_id = ? AND item = ?",
            (new_amount, user_id, item)
        )

    conn.commit()
    conn.close()
    return True


def get_inventory(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT item, amount FROM inventory WHERE user_id = ?",
        (user_id,)
    )
    rows = cur.fetchall()

    conn.close()
    return rows


# -----------------------------
# Cooldown Helpers
# -----------------------------
def get_cooldown(user_id: int, command: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT last_used FROM cooldowns WHERE user_id = ? AND command = ?",
        (user_id, command)
    )
    row = cur.fetchone()

    conn.close()
    return row["last_used"] if row else None


def set_cooldown(user_id: int, command: str, timestamp: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO cooldowns (user_id, command, last_used) VALUES (?, ?, ?)",
        (user_id, command, timestamp)
    )

    conn.commit()
    conn.close()
