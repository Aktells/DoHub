# db.py
from pathlib import Path
import streamlit as st
from passlib.hash import bcrypt
if USE_PG:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.errors import UniqueViolation

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
        if commit: conn.commit()
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
        if commit: conn.commit()
        conn.close()
        return data

def init_db():
    # Base table
    _exec("""
    CREATE TABLE IF NOT EXISTS users (
        id {} PRIMARY KEY {},
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """.format("SERIAL" if USE_PG else "INTEGER", "" if USE_PG else "AUTOINCREMENT"), commit=True)

    # Add unique index on LOWER(email) to block duplicates with different casing
    if USE_PG:
        _exec("CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique ON users (LOWER(email));", commit=True)
    else:
        # SQLite: case-insensitive unique using COLLATE NOCASE index
        _exec("CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique ON users (email COLLATE NOCASE);", commit=True)

def normalize_email(email: str) -> str:
    return (email or "").strip().lower()

def user_exists(email: str) -> bool:
    email = normalize_email(email)
    row = _exec(
        "SELECT 1 FROM users WHERE {}=?" .format("LOWER(email)" if USE_PG else "email")
            if not USE_PG else
        "SELECT 1 FROM users WHERE LOWER(email)=LOWER(%s)",
        (email,),
        fetchone=True
    )
    return bool(row)

def register_user(email: str, password: str, role="volunteer") -> bool:
    email = normalize_email(email)
    if not email or not password:
        return False

    # Pre-check avoids noisy exceptions & gives clearer UX
    if user_exists(email):
        return False

    pw_hash = bcrypt.hash(password)

    if USE_PG:
        try:
            _exec(
                "INSERT INTO users (email, password_hash, role) VALUES (%s,%s,%s)",
                (email, pw_hash, role),
                commit=True
            )
            return True
        except Exception as e:
            # If race-condition duplicate occurs, still return False
            if e.__class__.__name__ == "UniqueViolation":
                return False
            return False
    else:
        try:
            _exec(
                "INSERT INTO users (email, password_hash, role) VALUES (?,?,?)",
                (email, pw_hash, role),
                commit=True
            )
            return True
        except sqlite3.IntegrityError:
            return False

def validate_user(email: str, password: str):
    email = normalize_email(email)
    row = _exec(
        "SELECT password_hash, role FROM users WHERE {}=?".format("LOWER(email)" if USE_PG else "email")
            if not USE_PG else
        "SELECT password_hash, role FROM users WHERE LOWER(email)=LOWER(%s)",
        (email,),
        fetchone=True
    )
    if not row:
        return None
    pw_hash, role = row
    if bcrypt.verify(password, pw_hash):
        return {"email": email, "role": role}
    return None

def seed_demo_user():
    # Optional: only for DEMO mode
    if not DEMO:
        return
    if not user_exists("demo@dohub.in"):
        register_user("demo@dohub.in", "demo123", role="volunteer")



