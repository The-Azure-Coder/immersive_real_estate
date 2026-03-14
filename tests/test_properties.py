import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_create_property(client, db):
    # Mock services
    with patch("app.api.v1.endpoints.properties.upload_file", new_callable=AsyncMock) as mock_upload, \
         patch("app.api.v1.endpoints.properties.generate_3d_model", new_callable=AsyncMock) as mock_generate:
        
        mock_upload.return_value = "/uploads/property-images/test.jpg"
        mock_generate.return_value = "https://fake-s3-url/model.glb"
        
        # Register and login first as owner
        user_data = {
            "email": "owner@example.com",
            "password": "secretpassword",
            "full_name": "Owner User",
            "role": "owner"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Create property
        files = {
            "image": ("test.jpg", b"fake image content", "image/jpeg")
        }
        form_data = {
            "title": "Beautiful House",
            "location": "New York",
            "price": 500000,
            "land_size": 200.5
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/api/v1/properties/", data=form_data, files=files, headers=headers)
        # Note: the test client automatically prefixes with /api/v1 if included in the router, 
        # but here I included it in app.include_router(api_router, prefix="/api/v1")
        # and api_router has prefix="", wait let's check.
        
        # Actually in app/main.py: app.include_router(api_router, prefix="/api/v1")
        # And in app/api/v1/router.py: router = APIRouter()
        # So it should be /api/v1/properties/
        
        # Let's try /api/v1/properties/
        response = client.post("/api/v1/properties/", data=form_data, files=files, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Beautiful House"
        assert data["image_url"] == mock_upload.return_value
        assert data["model_3d_url"] == mock_generate.return_value

def test_list_properties(client, db):
    response = client.get("/api/v1/properties/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
