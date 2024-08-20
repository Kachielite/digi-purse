from app.core.security import create_token


def test_new_user(test_client, user_payload):
    response = test_client.post('/auth/create', json=user_payload)

    assert response.status_code == 201
    assert response.json().get("message") == "User created successfully"


def test_authenticate(test_client, user_payload):
    test_client.post('/auth/create', json=user_payload)
    response = test_client.post('/auth/token',
                                data={"username": user_payload.get('email'), "password": user_payload.get('password')})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user(test_client, user_payload):
    test_client.post('/auth/create', json=user_payload)
    token_response = test_client.post('/auth/token',
                                      data={"username": user_payload.get('email'),
                                            "password": user_payload.get('password')})

    token = token_response.json().get('access_token')
    response = test_client.get('/auth/me', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get('username') == user_payload.get('username')


def test_new_user_failure(test_client, bad_user_payload):
    response = test_client.post('/auth/create', json=bad_user_payload)

    assert response.status_code != 201
    assert response.json().get("detail") is not None


def test_authenticate_failure_with_wrong_password(test_client, user_payload):
    test_client.post('/auth/create', json=user_payload)
    response = test_client.post('/auth/token',
                                data={"username": user_payload.get('email'), "password": "wrong_password"})

    assert response.status_code == 401
    assert response.json().get("detail") == "Wrong Credentials"


def test_authenticate_failure_with_wrong_user(test_client, user_payload):
    test_client.post('/auth/create', json=user_payload)
    response = test_client.post('/auth/token',
                                data={"username": "test@mai.com", "password": "wrong_password"})

    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"

