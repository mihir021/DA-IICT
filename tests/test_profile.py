import pytest
from fastapi.testclient import TestClient
from api.main import app
import uuid

client = TestClient(app)

def test_profile_access():
    """
    Test full flow: Signup -> Login -> Profile Fetch
    """
    email = f"profile_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup
    client.post("/api/signup", json={"name": "Profile User", "email": email, "password": password})
    
    # 2. Login
    login_res = client.post("/api/login", json={"email": email, "password": password})
    token = login_res.json()["token"]
    
    # 3. Fetch Profile
    response = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["name"] == "Profile User"
    assert response.json()["email"] == email

def test_profile_unauthorized():
    """
    Test that fetching profile without token fails.
    """
    response = client.get("/api/profile")
    assert response.status_code == 401
