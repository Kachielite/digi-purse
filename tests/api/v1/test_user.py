from app.models.User import User


def get_token(client, user):
    client.post('/auth/create', json=user)
    response = client.post('/auth/token',
                           data={"username": user.get('email'), "password": user.get('password')})

    return response.json().get('access_token')


def create_user(client, user, token):
    return client.post('/users/add', headers={"Authorization": f"Bearer {token}"}, json=user)


def test_list_all_users(test_client, user_payload):
    token = get_token(test_client, user_payload)

    response = test_client.get('/users/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_all_users_by_normal_user(test_client, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    response = test_client.get('/users/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to view users"


def test_create_user_by_normal_user(test_client, normal_user_payload, user_payload_existing_email):
    token = get_token(test_client, normal_user_payload)

    response = test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"},
                                json=user_payload_existing_email)

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to create users"


def test_create_user_with_existing_email(test_client, user_payload, user_payload_existing_email):
    token = get_token(test_client, user_payload)

    response = test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"},
                                json=user_payload_existing_email)

    assert response.status_code == 400
    assert response.json().get("detail") == "User with the associated email already exist"


def test_create_user_with_existing_phone_number(test_client, user_payload, user_payload_existing_phone_number):
    token = get_token(test_client, user_payload)

    response = test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"},
                                json=user_payload_existing_phone_number)

    assert response.status_code == 400
    assert response.json().get("detail") == "User with the associated phone number already exist"


def test_create_user_with_existing_username(test_client, user_payload, user_payload_existing_username):
    token = get_token(test_client, user_payload)

    response = test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"},
                                json=user_payload_existing_username)

    assert response.status_code == 400
    assert response.json().get("detail") == "User with the associated username already exist"


def test_create_user(test_client, user_payload, normal_user_payload):
    token = get_token(test_client, user_payload)

    response = test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"},
                                json=normal_user_payload)

    assert response.status_code == 201
    assert response.json().get("message") == "User created successfully"


def test_update_user(test_client, user_payload, normal_user_payload, db_session, user_update_payload):
    token = get_token(test_client, user_payload)
    create_user(test_client, normal_user_payload, token)

    user_to_be_updated = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first()

    response = test_client.put(f"/users/{user_to_be_updated.id}", headers={"Authorization": f"Bearer {token}"},
                               json=user_update_payload)

    assert response.status_code == 200
    assert response.json().get("message") == "User role updated successfully"


def test_update_user_by_normal_user(test_client, user_payload, normal_user_payload, user_update_payload):
    token = get_token(test_client, normal_user_payload)

    response = test_client.put("/users/10", headers={"Authorization": f"Bearer {token}"},
                               json=user_update_payload)

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to update users"


def test_update_non_existing_user(test_client, user_payload, user_update_payload):
    token = get_token(test_client, user_payload)

    response = test_client.put("/users/10", headers={"Authorization": f"Bearer {token}"},
                               json=user_update_payload)

    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_delete_user_non_existing_user(test_client, user_payload):
    token = get_token(test_client, user_payload)

    response = test_client.delete('/users/10', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_delete_admin_user_admin_user(test_client, user_payload, admin_user_payload, db_session):
    token = get_token(test_client, admin_user_payload)
    create_user(test_client, user_payload, token)

    user_to_be_deleted = db_session.query(User).filter(User.email == user_payload.get("email")).first()

    response = test_client.delete(f"/users/{user_to_be_deleted.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get("detail") == "Only Sys admin can delete Admin users"


def test_delete_sys_user_admin_user(test_client, user_payload, sys_user_payload, db_session):
    token = get_token(test_client, user_payload)
    create_user(test_client, sys_user_payload, token)

    user_to_be_deleted = db_session.query(User).filter(User.email == sys_user_payload.get("email")).first()

    response = test_client.delete(f"/users/{user_to_be_deleted.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get("detail") == "Only Sys admin can delete a Sys admin user"


def test_delete_user(test_client, user_payload, normal_user_payload, db_session):
    token = get_token(test_client, user_payload)
    create_user(test_client, normal_user_payload, token)

    user_to_be_deleted = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first()

    response = test_client.delete(f"/users/{user_to_be_deleted.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get("message") == "User deleted successfully"
