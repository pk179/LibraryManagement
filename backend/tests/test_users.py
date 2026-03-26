import pytest


# Test that get users endpoint works correctly.
def test_get_users(client, admin_token, admin_headers):
    r = client.get("/api/users/", headers=admin_headers(admin_token))
    assert r.status_code == 200

    users = r.json()
    assert isinstance(users, list)
    assert len(users) > 0

    for user in users:
        assert user["id"] is not None
        assert isinstance(user["username"], str)
        assert user["role"] in ["admin", "user"]
        assert "password" not in user


# Test that get users endpoint requires admin role.
def test_get_users_requires_admin(client, user_token, user_headers):
    r = client.get("/api/users/", headers=user_headers(user_token))
    assert r.status_code == 403
    assert r.json()["detail"] == "Admin access required"

    r = client.get("/api/users/")
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that deleting user works correctly.
def test_delete_user(client, admin_token, admin_headers):
    r = client.delete("/api/users/2",
                      headers=admin_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["message"] == "User deleted successfully"

    users = client.get(
        "/api/users/", headers=admin_headers(admin_token)).json()
    assert all(user["id"] != 2 for user in users)

    data = {"username": "user", "password": "User12345"}
    r = client.post("/api/auth/login", json=data)
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid username or password"}


# Test that delete user endpoint requires admin role.
def test_delete_user_requires_admin(client, user_token, user_headers):
    r = client.delete("/api/users/1", headers=user_headers(user_token))
    assert r.status_code == 403
    assert r.json()["detail"] == "Admin access required"

    r = client.delete("/api/users/1")
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that deleting the same user twice fails.
def test_delete_user_twice(client, admin_token, admin_headers):
    r = client.delete("/api/users/2",
                      headers=admin_headers(admin_token))
    assert r.status_code == 200

    r = client.delete("/api/users/2",
                      headers=admin_headers(admin_token))
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


# Test that admin cannot delete their own account.
def test_delete_current_user(client, admin_token, admin_headers):
    r = client.delete("/api/users/1",
                      headers=admin_headers(admin_token))
    assert r.status_code == 400
    assert r.json()["detail"] == "Admin cannot delete themselves"


# Test that deleting a non-existing user fails.
@pytest.mark.parametrize("user_id", [4, 8, 999])
def test_delete_non_existing_user(client, admin_token, admin_headers, user_id):
    r = client.delete(f"/api/users/{user_id}",
                      headers=admin_headers(admin_token))
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


# Test that deleting a user with invalid input fails.
@pytest.mark.parametrize("user_id", ["admin", "user", "abc", None])
def test_delete_invalid_user(client, admin_token, admin_headers, user_id):
    r = client.delete(
        f"/api/users/{user_id}", headers=admin_headers(admin_token))
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] in ["int_parsing", "int_type"]
