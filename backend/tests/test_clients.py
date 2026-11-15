import pytest

def get_auth_token(client, email, password="password123", full_name="User", role="owner"):
    resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    })
    return resp.json()["access_token"]

def test_clients_crud_and_search(client):
    token = get_auth_token(client, "owner_clients@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create client
    create_payload = {
        "name": "Stark Industries",
        "company": "Stark Corp",
        "email": "tony@stark.com",
        "phone": "+1-555-0199",
        "notes": "Key enterprise account"
    }
    r_create = client.post("/api/v1/clients", json=create_payload, headers=headers)
    assert r_create.status_code == 201
    client_id = r_create.json()["id"]
    assert r_create.json()["name"] == "Stark Industries"
    assert r_create.json()["projects_count"] == 0

    # 2. List clients
    r_list = client.get("/api/v1/clients", headers=headers)
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1

    # 3. Search client by keyword
    r_search = client.get("/api/v1/clients?q=Stark", headers=headers)
    assert r_search.status_code == 200
    assert len(r_search.json()) == 1

    r_search_none = client.get("/api/v1/clients?q=NonExistent", headers=headers)
    assert r_search_none.status_code == 200
    assert len(r_search_none.json()) == 0

    # 4. Update client
    r_update = client.put(f"/api/v1/clients/{client_id}", json={
        "notes": "Updated engagement terms"
    }, headers=headers)
    assert r_update.status_code == 200
    assert r_update.json()["notes"] == "Updated engagement terms"

    # 5. Get client by ID
    r_get = client.get(f"/api/v1/clients/{client_id}", headers=headers)
    assert r_get.status_code == 200
    assert r_get.json()["id"] == client_id

    # 6. Delete client
    r_delete = client.delete(f"/api/v1/clients/{client_id}", headers=headers)
    assert r_delete.status_code == 200

    r_get_deleted = client.get(f"/api/v1/clients/{client_id}", headers=headers)
    assert r_get_deleted.status_code == 404

def test_clients_tenant_isolation(client):
    token_a = get_auth_token(client, "tenant_a@agency.com")
    token_b = get_auth_token(client, "tenant_b@agency.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant A creates a client
    r_create = client.post("/api/v1/clients", json={
        "name": "Secret Client A",
        "email": "confidential@clienta.com"
    }, headers=headers_a)
    client_a_id = r_create.json()["id"]

    # Tenant B lists clients - should not see Tenant A's client
    r_list_b = client.get("/api/v1/clients", headers=headers_b)
    ids_b = [c["id"] for c in r_list_b.json()]
    assert client_a_id not in ids_b

    # Tenant B directly queries Tenant A's client ID - must return 404
    r_get_b = client.get(f"/api/v1/clients/{client_a_id}", headers=headers_b)
    assert r_get_b.status_code == 404

    # Tenant B attempts to update Tenant A's client ID - must return 404
    r_update_b = client.put(f"/api/v1/clients/{client_a_id}", json={
        "name": "Hacked Name"
    }, headers=headers_b)
    assert r_update_b.status_code == 404

    # Tenant B attempts to delete Tenant A's client ID - must return 404
    r_delete_b = client.delete(f"/api/v1/clients/{client_a_id}", headers=headers_b)
    assert r_delete_b.status_code == 404
