from fastapi import status

def test_register_user(client, db):
    user_data = {
        "email": "test@example.com",
        "password": "secretpassword",
        "full_name": "Test User",
        "role": "buyer"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

def test_login_user(client, db):
    # Register first
    user_data = {
        "email": "login@example.com",
        "password": "secretpassword",
        "full_name": "Login User",
        "role": "owner"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
