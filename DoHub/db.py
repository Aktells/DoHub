import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize once
cred = credentials.Certificate("52715281a6b4dc26389f6107abbcde5ead55e9af")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Register user (NGO or volunteer)
def register_user(email, password, role="volunteer"):
    try:
        user = auth.create_user(email=email, password=password)
        # Save role in Firestore
        db.collection("users").document(user.uid).set({
            "email": email,
            "role": role
        })
        return True
    except Exception as e:
        print("Error registering:", e)
        return False

# Validate login (returns user info if valid)
def validate_user(email, password):
    try:
        # Firebase Auth handles password check on client-side normally,
        # but for server-side you can use Firebase REST API with email/password.
        user = auth.get_user_by_email(email)
        user_doc = db.collection("users").document(user.uid).get()
        return user_doc.to_dict() if user_doc.exists else None
    except Exception as e:
        print("Login error:", e)
        return None

# Store NGO details
def register_ngo(uid, details: dict):
    db.collection("ngos").document(uid).set(details)


