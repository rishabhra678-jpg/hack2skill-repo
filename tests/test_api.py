import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine, SessionLocal
import os

# Create a test client
client = TestClient(app)

def test_read_main():
    """Test the root endpoint serving the frontend."""
    response = client.get("/")
    assert response.status_code == 200
    # If frontend exists, it returns HTML, otherwise JSON message
    if os.path.exists("frontend/index.html"):
        assert "NutriMind" in response.text
    else:
        assert response.json()["message"] == "NutriMind API is running. Frontend not found."

def test_signup_login():
    """Test user signup and login flow."""
    # Unique email for each test run if needed, but we use a fresh DB
    email = "testuser@example.com"
    password = "testpassword123"
    
    # Signup
    signup_res = client.post("/api/auth/signup", json={
        "email": email,
        "password": password,
        "name": "Test User"
    })
    assert signup_res.status_code == 200
    data = signup_res.json()
    assert "token" in data
    assert data["user"]["email"] == email
    
    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    assert "token" in login_res.json()

def test_scan_food():
    """Test the AI food scan endpoint."""
    # Signup/Login to get token
    client.post("/api/auth/signup", json={
        "email": "scanner@example.com",
        "password": "password",
        "name": "Scanner User"
    })
    login_res = client.post("/api/auth/login", json={
        "email": "scanner@example.com",
        "password": "password"
    })
    token = login_res.json()["token"]
    
    # Scan pizza
    response = client.post(
        "/api/scan-food", 
        json={"food_name": "pizza"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["food_name"] == "Pizza"
    assert "calories" in data
    assert "health_score" in data
