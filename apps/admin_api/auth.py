import os

from django.contrib.auth.hashers import check_password
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from database.collections import ADMIN_USERS
from database.connection import get_database


TOKEN_MAX_AGE = 60 * 60 * 8


def _bootstrap_admin_payload() -> dict | None:
    email = os.getenv("ADMIN_BOOTSTRAP_EMAIL")
    password = os.getenv("ADMIN_BOOTSTRAP_PASSWORD")
    name = os.getenv("ADMIN_BOOTSTRAP_NAME", "Store Manager")
    if not email or not password:
        return None
    return {"name": name, "email": email, "password": password, "role": "operations_admin", "is_staff": True}


def authenticate_admin(email: str, password: str) -> dict | None:
    database = get_database()
    if database is not None:
        admin = database[ADMIN_USERS].find_one({"email": email, "is_staff": True}, {"_id": 0})
        if admin and check_password(password, admin.get("password_hash", "")):
            return {"name": admin.get("name", "Admin"), "email": admin["email"], "role": admin.get("role", "operations_admin"), "is_staff": True}

    bootstrap = _bootstrap_admin_payload()
    if bootstrap and email == bootstrap["email"] and password == bootstrap["password"]:
        return {key: value for key, value in bootstrap.items() if key != "password"}
    return None


def create_token(admin: dict) -> str:
    payload = {"email": admin["email"], "name": admin["name"], "role": admin["role"], "is_staff": True}
    return TimestampSigner().sign_object(payload)


def authenticate_request(request) -> dict | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None

    try:
        payload = TimestampSigner().unsign_object(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None

    if not payload.get("is_staff"):
        return None
    return payload
