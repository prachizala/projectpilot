import json
import pytest
from app.services.proposal_service import ProposalService

def get_auth_token(client, email):
    resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "password123",
        "full_name": "Agency Architect",
        "role": "owner"
    })
    return resp.json()["access_token"]

def test_proposal_generation_and_conversion(client):
    token = get_auth_token(client, "proposals_admin@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Setup Client
    r_client = client.post("/api/v1/clients", json={"name": "Cyberdyne", "email": "contracts@cyberdyne.com"}, headers=headers)
    client_id = r_client.json()["id"]

    # 1. Generate Proposal from raw client text
    raw_brief = (
        "Client needs a full automated e-commerce web platform.\n"
        "- Modern React storefront with high speed search\n"
        "- FastAPI backend with PostgreSQL and Stripe checkout\n"
        "- Automated stock inventory management\n"
        "- Admin analytics dashboard and order notifications"
    )
    gen_payload = {
        "title": "Cyberdyne E-Commerce Platform",
        "raw_requirements": raw_brief,
        "client_id": client_id,
        "target_budget": 12000.0
    }
    r_gen = client.post("/api/v1/proposals/generate", json=gen_payload, headers=headers)
    assert r_gen.status_code == 201
    prop_data = r_gen.json()
    prop_id = prop_data["id"]

    assert prop_data["title"] == "Cyberdyne E-Commerce Platform"
    assert prop_data["estimated_budget"] == 12000.0
    assert prop_data["status"] == "draft"

    milestones = json.loads(prop_data["milestones_json"])
    assert len(milestones) == 3
    assert milestones[0]["budget"] == 3000.0  # 25% of 12000
    assert milestones[1]["budget"] == 6000.0  # 50% of 12000
    assert milestones[2]["budget"] == 3000.0  # 25% of 12000

    # 2. Convert Proposal into active Project + Tasks
    r_conv = client.post(f"/api/v1/proposals/{prop_id}/convert", headers=headers)
    assert r_conv.status_code == 200
    project_data = r_conv.json()
    project_id = project_data["id"]

    assert project_data["title"] == "Cyberdyne E-Commerce Platform"
    assert project_data["budget"] == 12000.0
    assert project_data["tasks_count"] > 0

    # 3. Verify Tasks created under the project
    r_tasks = client.get(f"/api/v1/projects/{project_id}/tasks", headers=headers)
    assert r_tasks.status_code == 200
    tasks_list = r_tasks.json()
    assert len(tasks_list) >= 6
    for t in tasks_list:
        assert t["status"] == "todo"
        assert t["project_id"] == project_id

    # 4. Verify Proposal status updated to 'converted'
    r_get_prop = client.get(f"/api/v1/proposals/{prop_id}", headers=headers)
    assert r_get_prop.status_code == 200
    assert r_get_prop.json()["status"] == "converted"
