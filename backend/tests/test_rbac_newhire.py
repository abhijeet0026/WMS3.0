def test_nh_001_login(newhire_reno_client):
    response = newhire_reno_client.get("/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "NEW_HIRE"

def test_nh_002_own_stock(newhire_reno_client):
    response = newhire_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200

def test_nh_003_other_facility_stock(newhire_reno_client):
    response = newhire_reno_client.get("/v1/inventory?warehouse_id=COLUMBUS")
    assert response.status_code == 403

def test_nh_007_api_response_security(newhire_reno_client):
    response = newhire_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200
    for prod in response.json():
        assert prod.get("seller_name") is None

def test_nh_018_audit_log(newhire_reno_client):
    response = newhire_reno_client.get("/v1/audit/logs")
    assert response.status_code == 403

def test_nh_020_account_creation(newhire_reno_client):
    response = newhire_reno_client.post("/v1/auth/users", json={
        "username": "test_by_nh",
        "email": "test@test.com",
        "full_name": "Test",
        "password": "password123",
        "role": "NEW_HIRE",
        "facility_scope": "RENO"
    })
    assert response.status_code == 403
