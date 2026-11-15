import datetime
import pytest

def get_auth_token(client, email, password="password123", full_name="User", role="owner", client_id=None):
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    }
    if client_id is not None:
        payload["client_id"] = client_id
    resp = client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]

def test_projects_crud_and_status_filtering(client):
    token = get_auth_token(client, "project_owner@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create client first
    r_client = client.post("/api/v1/clients", json={
        "name": "Wayne Enterprises",
        "email": "bruce@wayne.com"
    }, headers=headers)
    client_id = r_client.json()["id"]

    # 1. Create project
    proj_payload = {
        "title": "Batmobile Telemetry System",
        "description": "High-speed encrypted telemetry dashboard",
        "status": "in_progress",
        "budget": 45000.0,
        "deadline": str(datetime.date.today() + datetime.timedelta(days=45)),
        "client_id": client_id
    }
    r_create = client.post("/api/v1/projects", json=proj_payload, headers=headers)
    assert r_create.status_code == 201
    proj_data = r_create.json()
    project_id = proj_data["id"]
    assert proj_data["title"] == "Batmobile Telemetry System"
    assert proj_data["client_name"] == "Wayne Enterprises"
    assert proj_data["tasks_count"] == 0

    # 2. List projects with status filter
    r_filter = client.get("/api/v1/projects?status=in_progress", headers=headers)
    assert r_filter.status_code == 200
    assert len(r_filter.json()) >= 1

    r_filter_empty = client.get("/api/v1/projects?status=completed", headers=headers)
    assert r_filter_empty.status_code == 200
    assert len(r_filter_empty.json()) == 0

    # 3. Update project status
    r_update = client.put(f"/api/v1/projects/{project_id}", json={
        "status": "in_review",
        "budget": 48000.0
    }, headers=headers)
    assert r_update.status_code == 200
    assert r_update.json()["status"] == "in_review"
    assert r_update.json()["budget"] == 48000.0

    # 4. Get project details
    r_get = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert r_get.status_code == 200
    assert r_get.json()["id"] == project_id

    # 5. Delete project
    r_delete = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
    assert r_delete.status_code == 200

    r_get_del = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert r_get_del.status_code == 404

def test_projects_cross_tenant_validation(client):
    token_a = get_auth_token(client, "agency_a@agency.com")
    token_b = get_auth_token(client, "agency_b@agency.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Agency A creates Client A
    r_client_a = client.post("/api/v1/clients", json={
        "name": "Client of A",
        "email": "client_a@test.com"
    }, headers=headers_a)
    client_a_id = r_client_a.json()["id"]

    # Agency B attempts to create a project linking Client A (must be rejected!)
    r_bad_proj = client.post("/api/v1/projects", json={
        "title": "Illicit Cross-Tenant Project",
        "client_id": client_a_id,
        "budget": 1000.0
    }, headers=headers_b)
    assert r_bad_proj.status_code == 404
    assert "does not exist or does not belong to your account" in r_bad_proj.json()["detail"]

def test_client_portal_role_isolation(client):
    owner_token = get_auth_token(client, "owner_portal@agency.com")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Owner creates 2 clients
    r_c1 = client.post("/api/v1/clients", json={"name": "Client Alpha", "email": "alpha@corp.com"}, headers=owner_headers)
    c1_id = r_c1.json()["id"]

    r_c2 = client.post("/api/v1/clients", json={"name": "Client Beta", "email": "beta@corp.com"}, headers=owner_headers)
    c2_id = r_c2.json()["id"]

    # Owner creates projects for each client
    r_p1 = client.post("/api/v1/projects", json={"title": "Alpha Project", "client_id": c1_id}, headers=owner_headers)
    p1_id = r_p1.json()["id"]

    r_p2 = client.post("/api/v1/projects", json={"title": "Beta Project", "client_id": c2_id}, headers=owner_headers)
    p2_id = r_p2.json()["id"]

    # Register client user for Client Alpha
    client_alpha_token = get_auth_token(
        client,
        email="contact@clientalpha.com",
        role="client",
        client_id=c1_id
    )
    alpha_headers = {"Authorization": f"Bearer {client_alpha_token}"}

    # Client Alpha lists projects: must ONLY see Alpha Project!
    r_alpha_projects = client.get("/api/v1/projects", headers=alpha_headers)
    assert r_alpha_projects.status_code == 200
    project_ids = [p["id"] for p in r_alpha_projects.json()]
    assert p1_id in project_ids
    assert p2_id not in project_ids

    # Client Alpha attempts to read Beta Project: must return 404!
    r_forbidden_get = client.get(f"/api/v1/projects/{p2_id}", headers=alpha_headers)
    assert r_forbidden_get.status_code == 404
