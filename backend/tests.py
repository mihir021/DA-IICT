import pytest
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

@pytest.fixture
def api_client():
    return APIClient()

def setup_mocks(mock_jwt, mock_get_db):
    user_id = "66175bf9e2c694a974b5c77a"
    mock_jwt.return_value = {"user_id": user_id}
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    colls = {
        "users": MagicMock(),
        "expenses": MagicMock(),
        "orders": MagicMock(),
        "products": MagicMock()
    }
    colls["users"].find_one.return_value = {"_id": ObjectId(user_id), "name": "AtlasUser", "email": "atlas@example.com"}
    colls["expenses"].find.return_value = []
    mock_db.__getitem__.side_effect = lambda name: colls.get(name, MagicMock())
    return mock_db

@patch('app.authentication.jwt.decode')
@patch('app.database.get_db')
def test_atlas_profile(mock_get_db, mock_jwt, api_client):
    setup_mocks(mock_jwt, mock_get_db)
    response = api_client.get('/api/profile/', HTTP_AUTHORIZATION='Bearer token')
    assert response.status_code == 200
    assert response.data["name"] == "AtlasUser"
