# db.py  — works on Streamlit Cloud (Passlib), PG or SQLite, demo-safe
from pathlib import Path
import streamlit as st

# ---- DEMO toggle (safe if config.py is missing) ----
try:
    from config import DEMO  # optional
except Exception:
    DEMO = False

# ---- Auth hashing (pure Python) ----
from passlib.hash import bcrypt

# ---- Choose backend: Postgres if secrets present & not demo; else SQLite ----
REQUIRED_PG_KEYS = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASS")
USE_PG = (not DEMO) and all(k in st.secrets for k in REQUIRED_PG_KEYS)

# ---- Minimal SQL helpers per backend (defined AFTER USE_PG exists) ----
if USE_PG:
    import psycopg2

    def get_conn():
        return psycopg2.connect(
            host=st.secrets["DB_HOST"],
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASS"],
            port=int(st.secrets.get("DB_PORT", 5432)),
        )

    def _exec(q, params=None, commit=False, fetchone=False):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(q, params or ())
        data = cur.fetchone() if fetchone else None
        if commit:
            conn.commit()
        conn.close()
        return data

else:
    import sqlite3
    DB_PATH = Path(__file__).with_name("users.db")

    def get_conn():
        return sqlite3.connect(DB_PATH)

    def _exec(q, params=None, commit=False, fetchone=False):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(q, params or ())
        data = cur.fetchone() if fetchone else None
        if commit:
            conn.commit()
        conn.close()
        return data

# ---- Schema & operations ----
def init_db():
    _exec(
        """
        CREATE TABLE IF NOT EXISTS users (
            id {} PRIMARY KEY {},
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """.format("SERIAL" if USE_PG else "INTEGER", "" if USE_PG else "AUTOINCREMENT"),
        commit=True,
    )
    # Unique (case-insensitive) email
    if USE_PG:
        _exec("CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique ON users (LOWER(email));", commit=True)
    else:
        _exec("CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique ON users (email COLLATE NOCASE);", commit=True)

def _norm_email(email: str) -> str:
    return (email or "").strip().lower()

def user_exists(email: str) -> bool:
    email = _norm_email(email)
    if USE_PG:
        row = _exec("SELECT 1 FROM users WHERE LOWER(email)=LOWER(%s)", (email,), fetchone=True)
    else:
        row = _exec("SELECT 1 FROM users WHERE email=?", (email,), fetchone=True)
    return bool(row)

def register_user(email: str, password: str, role="volunteer") -> bool:
    email = _norm_email(email)
    if not email or not password:
        return False
    if user_exists(email):
        return False
    pw_hash = bcrypt.hash(password)
    try:
        if USE_PG:
            _exec("INSERT INTO users (email, password_hash, role) VALUES (%s,%s,%s)",
                  (email, pw_hash, role), commit=True)
        else:
            _exec("INSERT INTO users (email, password_hash, role) VALUES (?,?,?)",
                  (email, pw_hash, role), commit=True)
        return True
    except Exception:
        return False

def validate_user(email: str, password: str):
    email = _norm_email(email)
    if USE_PG:
        row = _exec("SELECT password_hash, role FROM users WHERE LOWER(email)=LOWER(%s)", (email,), fetchone=True)
    else:
        row = _exec("SELECT password_hash, role FROM users WHERE email=?", (email,), fetchone=True)
    if not row:
        return None
    pw_hash, role = row
    return {"email": email, "role": role} if bcrypt.verify(password, pw_hash) else None

def seed_demo_user():
    # Only seed when DEMO=1 (optional)
    if not DEMO:
        return
    if not user_exists("demo@dohub.in"):
        register_user("demo@dohub.in", "demo123", role="volunteer")

