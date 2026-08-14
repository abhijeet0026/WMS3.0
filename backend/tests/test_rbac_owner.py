def test_own_001_owner_login(owner_client):
    response = owner_client.get("/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "OWNER"

def test_own_002_view_reno_stock(owner_client):
    response = owner_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200
    assert len(response.json()) > 0
    for item in response.json():
        assert item["warehouse_id"] == "RENO"

def test_own_003_view_columbus_stock(owner_client):
    response = owner_client.get("/v1/inventory?warehouse_id=COLUMBUS")
    assert response.status_code == 200
    assert len(response.json()) > 0
    for item in response.json():
        assert item["warehouse_id"] == "COLUMBUS"

def test_own_004_switch_facilities(owner_client):
    r1 = owner_client.get("/v1/inventory?warehouse_id=RENO")
    r2 = owner_client.get("/v1/inventory?warehouse_id=COLUMBUS")
    assert r1.status_code == 200 and r2.status_code == 200

def test_own_005_view_seller_identity(owner_client):
    response = owner_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200
    assert "seller_name" in response.json()[0]

def test_own_014_view_full_audit_log(owner_client):
    response = owner_client.get("/v1/audit/logs")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_own_017_excel_reconciliation(owner_client):
    response = owner_client.get("/v1/migration/issues")
    assert response.status_code == 200

def test_own_018_create_owner(owner_client):
    payload = {
        "username": "new_owner",
        "email": "new_owner@test.com",
        "full_name": "New Owner",
        "password": "password123",
        "role": "OWNER"
    }
    response = owner_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 201

def test_own_019_create_manager(owner_client):
    payload = {
        "username": "new_mgr_reno",
        "email": "new_mgr@test.com",
        "full_name": "New Mgr",
        "password": "password123",
        "role": "MANAGER",
        "facility_scope": "RENO"
    }
    response = owner_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 201

def test_own_022_deactivate_account(owner_client):
    # we created new_mgr_reno above
    users = owner_client.get("/v1/auth/users").json()
    mgr = next(u for u in users if u["username"] == "new_mgr_reno")
    response = owner_client.patch(f"/v1/auth/users/{mgr['id']}/status", json={"status": "INACTIVE"})
    assert response.status_code == 200
    
    # Verify they can't login
    from fastapi.testclient import TestClient
    from main import app
    c = TestClient(app)
    login_resp = c.post("/v1/auth/login", json={"username": "new_mgr_reno", "password": "password123"})
    assert login_resp.status_code == 403

def test_own_025_assistant_text(owner_client):
    response = owner_client.post("/v1/assistant/chat", json={"user_query": "What is the stock in Reno?", "warehouse_id": "RENO"})
    assert response.status_code == 200
    assert "response" in response.json() or "spoken_response" in response.json()


def test_own_026_assistant_present_query(owner_client):
    response = owner_client.post("/v1/assistant/chat", json={"user_query": "Is SKU-101 present in Reno?", "warehouse_id": "RENO"})
    assert response.status_code == 200
    body = response.json()
    text = body.get("spoken_response", "").lower()
    assert "sku-101" in text or "wireless" in text
    assert "yes" in text or "present" in text or "we have" in text


def test_own_027_assistant_all_warehouse_sku_query(owner_client):
    response = owner_client.post("/v1/assistant/chat", json={"user_query": "How many SKU-102 do we have and where?", "warehouse_id": "ALL"})
    assert response.status_code == 200
    text = response.json().get("spoken_response", "")
    assert "SKU-102" in text or "sku-102" in text.lower()
    assert "RENO" in text or "Columbus" in text or "warehouse" in text
    assert "No inventory found" not in text
