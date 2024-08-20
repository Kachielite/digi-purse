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
                     data={"username": user_payload.get('email'), "password": user_payload.get('password')})

    token = token_response.json().get('access_token')
    response = test_client.get('/auth/me', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get('username') == user_payload.get('username')

