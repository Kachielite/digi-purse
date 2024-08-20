from fastapi import status


def test_health_route(test_client):
    response = test_client.get('/health')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "System Healthy"}
