import sqlite3, bcrypt
import smtplib
from email.mime.text import MIMEText

ADMIN_EMAIL = "apoorvkh18@gmail.com"      # <-- change this
SMTP_SERVER = "smtp.gmail.com"              # Gmail SMTP
SMTP_PORT = 587
SMTP_USER = "apoorvkh18@gmail.com"        # same as ADMIN_EMAIL
SMTP_PASS = "cebw vbgh mnds xskn "             # Gmail app password

def send_admin_email(subject, body):
    """Send an email to the admin when a new NGO registers."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ADMIN_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email failed:", e)
        return False

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )
    """)
    conn.commit()
    conn.close()

def register_user(email, password, role="volunteer"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cur.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                    (email, password_hash, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # email already exists

def validate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash, role FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        return {"email": email, "role": row[1]}
    return None
