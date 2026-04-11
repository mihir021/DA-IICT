import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.connection import get_db
from bson import ObjectId
import uuid

client = TestClient(app)
db = get_db()

def test_signup_success():
    """
    Test that a valid user can sign up successfully.
    """
    unique_email = f"test_{uuid.uuid4()}@example.com"
    payload = {
        "name": "Test User",
        "email": unique_email,
        "password": "password123"
    }
    
    response = client.post("/api/signup", json=payload)
    
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"
    
    # Verify user exists in DB
    user = db.users.find_one({"email": unique_email})
    assert user is not None
    assert user["name"] == "Test User"

def test_signup_duplicate_email():
    """
    Test that signing up with an existing email fails.
    """
    email = "duplicate@example.com"
    db.users.delete_one({"email": email}) # Ensure clean state
    
    payload = {"name": "User 1", "email": email, "password": "password123"}
    client.post("/api/signup", json=payload)
    
    # Attempt second signup with same email
    response = client.post("/api/signup", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
