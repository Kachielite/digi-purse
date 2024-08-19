from fastapi.testclient import TestClient
from fastapi import status

from app.main import app

client = TestClient(app)


def test_health_route():
    response = client.get('/health')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "System Healthy"}
