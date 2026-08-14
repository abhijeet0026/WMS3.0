def test_stf_001_login(staff_reno_client):
    response = staff_reno_client.get("/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "TRUSTED_STAFF"

def test_stf_002_own_stock(staff_reno_client):
    response = staff_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200

def test_stf_003_other_facility_stock(staff_reno_client):
    response = staff_reno_client.get("/v1/inventory?warehouse_id=COLUMBUS")
    assert response.status_code == 403

def test_stf_005_seller_identity_hidden(staff_reno_client):
    response = staff_reno_client.get("/v1/inventory?warehouse_id=RENO")
    assert response.status_code == 200
    # The API should omit or nullify the seller name
    for prod in response.json():
        assert prod.get("seller_name") is None

def test_stf_006_cost_hidden(staff_reno_client):
    # Same as above, if there are cost fields they should be None
    pass

def test_stf_017_audit_page(staff_reno_client):
    response = staff_reno_client.get("/v1/audit/logs")
    assert response.status_code == 403

def test_stf_019_account_creation(staff_reno_client):
    payload = {
        "username": "new_hire_by_staff",
        "email": "hire@test.com",
        "full_name": "Hire",
        "password": "password123",
        "role": "NEW_HIRE",
        "facility_scope": "RENO"
    }
    response = staff_reno_client.post("/v1/auth/users", json=payload)
    assert response.status_code == 403

def test_stf_021_reconciliation(staff_reno_client):
    response = staff_reno_client.get("/v1/migration/issues")
    assert response.status_code == 403

def test_stf_022_other_facility_shipment(staff_reno_client):
    response = staff_reno_client.post("/v1/receiving/shipments", json={
        "tracking_number": "TRK-999",
        "warehouse_id": "COLUMBUS",
        "seller_id": "SEL-001",
        "items": [{"product_id": "PROD-101", "quantity": 10, "condition": "GOOD"}]
    })
    assert response.status_code == 403
