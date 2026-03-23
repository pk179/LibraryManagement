import pytest
from fastapi.testclient import TestClient
from api.main import app
import database
import os

TEST_DB_NAME = "test.db"


# Create a new database and seed it with initial data.
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    database.DB_NAME = TEST_DB_NAME

    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

    database.init_db()
    database.seed_db()

    yield


# Reset the database before each test.
@pytest.fixture(scope="function", autouse=True)
def reset_db():
    database.reset_db()
    yield


# Provide a test client for making API requests.
@pytest.fixture(scope="session")
def client():
    return TestClient(app)


# Provide tokens for admin and regular user to test authenticated endpoints.
@pytest.fixture(scope="function")
def admin_token(client):
    data = {"username": "admin", "password": "Admin123"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="function")
def user_token(client):
    data = {"username": "user", "password": "User12345"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 200
    return r.json()["access_token"]


# Helper fixture to create auth headers for requests.
@pytest.fixture
def auth_header():
    def _auth(token):
        return {"Authorization": f"Bearer {token}"}
    return _auth
