import pytest
import os
import sys
import sqlite3

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set a test database URL
TEST_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_wms.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Create test engine and session
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch the database module BEFORE importing the app
import core.database.database as database
database.engine = test_engine
database.SessionLocal = TestingSessionLocal
database.DATABASE_URL = TEST_DATABASE_URL

from main import app
from core.database.database import Base
from core.apis.api import seed_initial_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Remove existing test DB if any
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Seed initial data for testing
    seed_initial_data()
    
    yield
    
    # Teardown
    test_engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture(scope="module")
def client():
    # TestClient context manager triggers startup/shutdown lifespan if needed
    with TestClient(app) as c:
        yield c

def get_auth_client(username, password="password123"):
    client = TestClient(app)
    response = client.post("/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, f"Failed to login {username}: {response.text}"
    token = response.json().get("access_token")
    if token:
        client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture(scope="module")
def owner_client():
    return get_auth_client("dan_owner")  # api.py seed: dan_owner / password123

@pytest.fixture(scope="module")
def manager_reno_client():
    return get_auth_client("manager_reno")  # api.py seed: manager_reno / password123

@pytest.fixture(scope="module")
def manager_columbus_client():
    return get_auth_client("manager_columbus")  # api.py seed: manager_columbus / password123

@pytest.fixture(scope="module")
def staff_reno_client():
    return get_auth_client("staff_reno")  # api.py seed: staff_reno / password123

@pytest.fixture(scope="module")
def staff_columbus_client():
    return get_auth_client("staff_columbus")  # api.py seed: staff_columbus / password123

@pytest.fixture(scope="module")
def newhire_reno_client():
    return get_auth_client("newhire_reno")  # api.py seed: newhire_reno / password123

@pytest.fixture(scope="module")
def newhire_columbus_client():
    return get_auth_client("newhire_columbus")  # api.py seed: newhire_columbus / password123
