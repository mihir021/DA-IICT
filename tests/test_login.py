import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.connection import get_db
import uuid

client = TestClient(app)
db = get_db()

def test_login_success():
    """
    Test that a registered user can log in and get a token.
    """
    email = f"login_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup
    client.post("/api/signup", json={"name": "Login Tester", "email": email, "password": password})
    
    # 2. Login
    response = client.post("/api/login", json={"email": email, "password": password})
    
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["name"] == "Login Tester"

def test_login_invalid_credentials():
    """
    Test that wrong password fails login.
    """
    response = client.post("/api/login", json={"email": "nonexistent@example.com", "password": "wrong"})
    assert response.status_code == 401
