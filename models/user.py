"""
models/user.py
──────────────
User model – handles all DB operations for the 'users' collection.

Collection schema:
  {
    _id:        ObjectId  (auto by MongoDB)
    name:       str
    email:      str  (unique, lowercase)
    password:   str  (bcrypt hashed)
    created_at: datetime
  }
"""

from datetime import datetime, timezone
import bcrypt
from bson import ObjectId
from db import get_db


def create_user(name: str, email: str, password: str) -> dict | None:
    """
    Create a new user. Returns the inserted document or None if email exists.
    Password is hashed with bcrypt before storing.
    """
    db = get_db()

    # Check for duplicate email (case-insensitive)
    if db.users.find_one({"email": email.lower()}):
        return None  # Email already registered

    # Hash the password – bcrypt auto-generates a salt
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user_doc = {
        "name": name.strip(),
        "email": email.lower().strip(),
        "password": hashed,          # stored as bytes
        "created_at": datetime.now(timezone.utc),
    }

    result = db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


def find_user_by_email(email: str) -> dict | None:
    """Fetch a user document by email (case-insensitive)."""
    db = get_db()
    return db.users.find_one({"email": email.lower().strip()})


def find_user_by_id(user_id: str) -> dict | None:
    """Fetch a user document by its MongoDB ObjectId string."""
    db = get_db()
    try:
        return db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Compare a plain-text password against the stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
