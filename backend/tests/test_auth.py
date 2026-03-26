import os
import pytest


# Test registering a new user with valid data.
def test_register_new_user(client):
    data = {"username": "user2", "password": "User12345", "role": "user"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 201

    response = r.json()

    assert response["message"] == "User registered"
    assert response["user"]["id"] is not None
    assert response["user"]["username"] == data["username"]
    assert response["user"]["role"] == data["role"]


# Test registering a user with a username that already exists.
def test_register_duplicate_username(client):
    data = {"username": "admin", "password": "Admin123", "role": "admin"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 409
    assert r.json() == {"detail": "Username already exists"}


# Test registering a user with an invalid username (too short).
def test_register_invalid_username(client):
    data = {"username": "a", "password": "User12345", "role": "user"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 400
    assert r.json() == {
        "detail": "Username must be 3-30 characters and contain only letters, digits or underscore."}


# Test registering a user with no password or role.
def test_register_missing_fields(client):
    data = {"username": "user2"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 422


# Test registering a user with an invalid role.
def test_register_invalid_role(client):
    data = {"username": "user2", "password": "User12345", "role": "invalid"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 400
    assert r.json() == {"detail": "Role must be one of: admin, user."}


# Test registering a user with a weak password.
@pytest.mark.parametrize("password", ["abc", "password", "12345678"])
def test_register_weak_password(client, password):
    data = {"username": "user2", "password": password, "role": "user"}
    r = client.post("/api/auth/register", json=data)
    assert r.status_code == 400


# Test logging in with correct credentials.
def test_login_success(client):
    data = {"username": "admin", "password": "Admin123"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 200
    assert "access_token" in r.json()


# Test logging in with an incorrect password.
def test_login_bad_password(client):
    data = {"username": "admin", "password": "Admin1234"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid username or password"}


# Test logging in with a username that does not exist.
def test_login_nonexistent_user(client):
    data = {"username": "user5", "password": "User12345"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid username or password"}


# Test that the JWT token contains the expected payload data.
def test_jwt_payload(client):
    data = {"username": "admin", "password": "Admin123"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 200
    token = r.json()["access_token"]

    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    # Decode the JWT token to verify its payload
    from jose import jwt
    payload = jwt.decode(token, options={
                         "verify_signature": False}, key=SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "1"
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"
