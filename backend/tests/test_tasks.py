import pytest

def get_auth_token(client, email):
    resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "password123",
        "full_name": "Task Owner",
        "role": "owner"
    })
    return resp.json()["access_token"]

def test_tasks_crud_and_kanban_reordering(client):
    token = get_auth_token(client, "task_tester@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Setup Client & Project
    r_client = client.post("/api/v1/clients", json={"name": "Acme", "email": "acme@test.com"}, headers=headers)
    client_id = r_client.json()["id"]

    r_proj = client.post("/api/v1/projects", json={"title": "Sprint 1", "client_id": client_id}, headers=headers)
    proj_id = r_proj.json()["id"]

    # 1. Create Tasks in 'todo' column
    t1 = client.post(f"/api/v1/projects/{proj_id}/tasks", json={"title": "Task 1", "status": "todo"}, headers=headers).json()
    t2 = client.post(f"/api/v1/projects/{proj_id}/tasks", json={"title": "Task 2", "status": "todo"}, headers=headers).json()
    t3 = client.post(f"/api/v1/projects/{proj_id}/tasks", json={"title": "Task 3", "status": "todo"}, headers=headers).json()

    assert t1["position"] == 0
    assert t2["position"] == 1
    assert t3["position"] == 2

    # 2. Reorder within same column: Move Task 3 to position 0
    r_move_same = client.patch(f"/api/v1/tasks/{t3['id']}/position", json={
        "status": "todo",
        "position": 0
    }, headers=headers)
    assert r_move_same.status_code == 200

    # Verify positions: t3 -> 0, t1 -> 1, t2 -> 2
    tasks = client.get(f"/api/v1/projects/{proj_id}/tasks", headers=headers).json()
    todo_tasks = [t for t in tasks if t["status"] == "todo"]
    pos_map = {t["title"]: t["position"] for t in todo_tasks}
    assert pos_map["Task 3"] == 0
    assert pos_map["Task 1"] == 1
    assert pos_map["Task 2"] == 2

    # 3. Move Task 1 to another column ('in_progress') at position 0
    r_move_diff = client.patch(f"/api/v1/tasks/{t1['id']}/position", json={
        "status": "in_progress",
        "position": 0
    }, headers=headers)
    assert r_move_diff.status_code == 200

    tasks_after = client.get(f"/api/v1/projects/{proj_id}/tasks", headers=headers).json()
    inp_tasks = [t for t in tasks_after if t["status"] == "in_progress"]
    todo_after = [t for t in tasks_after if t["status"] == "todo"]

    assert len(inp_tasks) == 1
    assert inp_tasks[0]["id"] == t1["id"]
    # Todo column closed the gap: Task 3 is 0, Task 2 is now 1
    todo_map = {t["title"]: t["position"] for t in todo_after}
    assert todo_map["Task 3"] == 0
    assert todo_map["Task 2"] == 1

    # 4. Delete Task 3
    r_del = client.delete(f"/api/v1/tasks/{t3['id']}", headers=headers)
    assert r_del.status_code == 200

    # Remaining todo task (Task 2) should rebalance to position 0
    final_tasks = client.get(f"/api/v1/projects/{proj_id}/tasks", headers=headers).json()
    remaining_todo = [t for t in final_tasks if t["status"] == "todo"]
    assert len(remaining_todo) == 1
    assert remaining_todo[0]["title"] == "Task 2"
    assert remaining_todo[0]["position"] == 0
