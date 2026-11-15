import pytest

def get_auth_token(client, email):
    resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "password123",
        "full_name": "Executive User",
        "role": "owner"
    })
    return resp.json()["access_token"]

def test_dashboard_metrics(client):
    token = get_auth_token(client, "ceo@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Query metrics endpoint
    r = client.get("/api/v1/dashboard/metrics", headers=headers)
    assert r.status_code == 200
    data = r.json()

    assert "active_projects" in data
    assert "total_clients" in data
    assert "overdue_tasks" in data
    assert "total_revenue" in data
    assert "pending_revenue" in data
    assert "project_status_breakdown" in data
    assert "monthly_revenue" in data
    assert isinstance(data["monthly_revenue"], list)
