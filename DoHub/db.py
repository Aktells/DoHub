# db.py — Firebase-based database layer

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests

# -----------------------------
# INIT FIREBASE
# -----------------------------
if not firebase_admin._apps:
    key_json = os.getenv("FIREBASE_KEY")
    if not key_json:
        raise RuntimeError("❌ FIREBASE_KEY not found in environment variables.")
    
    key_dict = json.loads(key_json)
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# USER MANAGEMENT
# -----------------------------

def register_user(email: str, password: str, role: str = "volunteer") -> bool:
    """
    Register a new user in Firebase Auth + Firestore.
    """
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "email": email,
            "role": role
        })
        return True
    except Exception as e:
        print("Error registering user:", e)
        return False


def validate_user(email: str, password: str) -> dict | None:
    """
    Validate login using Firebase Auth REST API.
    Requires FIREBASE_API_KEY in env.
    """
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        raise RuntimeError("❌ FIREBASE_API_KEY not found in environment variables.")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        uid = data["localId"]

        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        print("Login error:", e)
        return None


# -----------------------------
# NGO MANAGEMENT
# -----------------------------

def register_ngo(uid: str, details: dict) -> bool:
    """
    Store NGO details in Firestore under ngos/{uid}.
    """
    try:
        db.collection("ngos").document(uid).set(details)
        return True
    except Exception as e:
        print("Error registering NGO:", e)
        return False


def get_ngo(uid: str) -> dict | None:
    """
    Fetch NGO details by uid.
    """
    try:
        doc = db.collection("ngos").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print("Error fetching NGO:", e)
        return None


# -----------------------------
# DEBUG HELPER
# -----------------------------
def check_connection():
    """
    Debug function to verify Firebase connection.
    """
    try:
        # Attempt a simple query
        users = db.collection("users").limit(1).get()
        return f"✅ Firebase connected. Found {len(users)} user(s)."
    except Exception as e:
        return f"❌ Firebase connection failed: {e}"
