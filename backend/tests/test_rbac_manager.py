def test_mgr_001_login(manager_reno_client):
    response = manager_reno_client.get("/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "MANAGER"
    assert response.json()["facility_scope"] == "RENO"

def test_mgr_002_own_facility_stock(manager_reno_client):
    response = manager_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200

def test_mgr_003_other_facility_stock(manager_reno_client):
    response = manager_reno_client.get("/v1/inventory?warehouse_id=COLUMBUS")
    assert response.status_code == 403

def test_mgr_005_seller_identity(manager_reno_client):
    response = manager_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200
    assert "seller_name" in response.json()[0]

def test_mgr_015_own_audit_log(manager_reno_client):
    response = manager_reno_client.get("/v1/audit/logs?warehouse_id=RENO")
    assert response.status_code == 200

def test_mgr_016_other_facility_audit(manager_reno_client):
    response = manager_reno_client.get("/v1/audit/logs?warehouse_id=COLUMBUS")
    assert response.status_code == 403

def test_mgr_017_create_trusted_staff(manager_reno_client):
    payload = {
        "username": "new_staff_reno_by_mgr",
        "email": "staff@test.com",
        "full_name": "New Staff",
        "password": "password123",
        "role": "TRUSTED_STAFF",
        "facility_scope": "RENO"
    }
    response = manager_reno_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 201

def test_mgr_019_create_manager(manager_reno_client):
    payload = {
        "username": "hacker_mgr",
        "email": "hack@test.com",
        "full_name": "Hacker",
        "password": "password123",
        "role": "MANAGER",
        "facility_scope": "RENO"
    }
    response = manager_reno_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 403

def test_mgr_021_create_staff_other_facility(manager_reno_client):
    payload = {
        "username": "sneaky_staff_col",
        "email": "sneak@test.com",
        "full_name": "Sneak",
        "password": "password123",
        "role": "TRUSTED_STAFF",
        "facility_scope": "COLUMBUS"
    }
    response = manager_reno_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 403

def test_mgr_026_assistant_other_facility(manager_reno_client):
    response = manager_reno_client.post("/v1/assistant/chat", json={
        "user_query": "Show me COLUMBUS stock for headphones",
        "voice_input": False
    })
    assert response.status_code == 403

def test_mgr_028_direct_api_bypass(manager_reno_client):
    # Try to reconcile Columbus issue as Reno manager
    response = manager_reno_client.post("/v1/migration/reconcile", json={"issue_id": "ISS-002", "actual_physical_quantity": 10, "notes": "test"})
    assert response.status_code == 403
