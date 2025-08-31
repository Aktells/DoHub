import bcrypt
import smtplib
from email.mime.text import MIMEText
from supabase import create_client, Client
import os

# --- Supabase setup ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fzklrmnfnvnwiypgomgq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # keep secret!
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Email config ---
ADMIN_EMAIL = "apoorvkh18@gmail.com"      # <-- change this
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "apoorvkh18@gmail.com"
SMTP_PASS = "cebw vbgh mnds xskn "        # Gmail app password

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

# --- User functions ---
def register_user(email, password, role="volunteer"):
    """Insert a new user in Supabase."""
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        response = supabase.table("users").insert({
            "email": email,
            "password_hash": password_hash,
            "role": role
        }).execute()
        return True if response.data else False
    except Exception as e:
        print("Register failed:", e)
        return False

def validate_user(email, password):
    """Check credentials against Supabase."""
    try:
        response = supabase.table("users").select("password_hash, role").eq("email", email).execute()
        if response.data:
            row = response.data[0]
            if bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
                return {"email": email, "role": row["role"]}
        return None
    except Exception as e:
        print("Validation failed:", e)
        return None


