import pytest
from app.core.security import hash_password, verify_password, decode_token

def test_password_hashing():
    raw_password = "supersecretpassword123"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_signup_success(client):
    payload = {
        "email": "alex@agency.com",
        "password": "securepassword123",
        "full_name": "Alex Mercer",
        "role": "owner"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alex@agency.com"
    assert data["user"]["full_name"] == "Alex Mercer"
    assert data["user"]["role"] == "owner"

def test_signup_duplicate_email(client):
    payload = {
        "email": "duplicate@agency.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "role": "owner"
    }
    r1 = client.post("/api/v1/auth/signup", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/signup", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

def test_login_flow(client):
    # Register user
    signup_payload = {
        "email": "login_test@agency.com",
        "password": "mypassword456",
        "full_name": "Login Tester",
        "role": "owner"
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    # Valid login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "login_test@agency.com",
        "password": "mypassword456"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # Invalid login password
    bad_login = client.post("/api/v1/auth/login", json={
        "email": "login_test@agency.com",
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401

    # Verify /me endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "login_test@agency.com"

    # Test refresh token endpoint
    refresh_resp = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

def test_protected_route_unauthorized(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401

    bad_resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert bad_resp.status_code == 401
