import uuid

from app.models.User import User
from app.models.Wallet import Wallet


def get_token(client, user):
    client.post('/auth/create', json=user)
    response = client.post('/auth/token',
                           data={"username": user.get('email'), "password": user.get('password')})

    return response.json().get('access_token')


def create_user(client, user, token):
    return client.post('/users/add', headers={"Authorization": f"Bearer {token}"}, json=user)


def test_create_wallet(test_client, user_payload, normal_user_payload, db_session):
    token = get_token(test_client, user_payload)

    test_client.post('/auth/create', json=normal_user_payload)

    normal_user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    wallet_payload = {
        "user_id": normal_user_id,
        "user_phone_number": normal_user_payload.get('phone_number')
    }

    response = test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    assert response.status_code == 201
    assert response.json().get("message") == "Wallet created successfully"


def test_creating_wallet_for_existing_user(test_client, user_payload, normal_user_payload, db_session):
    token = get_token(test_client, user_payload)

    create_user(test_client, normal_user_payload, token)

    normal_user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    wallet_payload = {
        "user_id": normal_user_id,
        "user_phone_number": normal_user_payload.get('phone_number')
    }

    test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    response = test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    assert response.status_code == 400
    assert response.json().get("detail") == "User already has a wallet"


def test_creating_wallet_by_normal_user(test_client, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    wallet_payload = {
        "user_id": 10,
        "user_phone_number": "2349069943111"
    }

    response = test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to create wallets"


def test_read_all_wallets(test_client, user_payload, normal_user_payload, admin_user_payload, db_session):
    token = get_token(test_client, user_payload)

    create_user(test_client, normal_user_payload, token)
    create_user(test_client, admin_user_payload, token)

    normal_user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id
    admin_user_payload = db_session.query(User).filter(User.email == admin_user_payload.get("email")).first().id

    normal_user_wallet_payload = {
        "user_id": normal_user_id,
        "user_phone_number": normal_user_payload.get('phone_number')
    }

    admin_wallet_payload = {
        "user_id": admin_user_payload,
        "user_phone_number": normal_user_payload.get('phone_number')
    }

    test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=normal_user_wallet_payload)
    test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=admin_wallet_payload)

    response = test_client.get('/wallets/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_reading_all_wallet_by_normal_user(test_client, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    response = test_client.get('/wallets/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to read wallets"


def test_reading_wallet_details(test_client, user_payload, normal_user_payload, db_session):
    token = get_token(test_client, user_payload)

    create_user(test_client, normal_user_payload, token)

    normal_user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    wallet_payload = {
        "user_id": normal_user_id,
        "user_phone_number": normal_user_payload.get('phone_number')
    }

    test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    response = test_client.get(f'/wallets/details?user_id={normal_user_id}',
                               headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get("user_id") == normal_user_id
    assert response.json().get("user_phone_number") == normal_user_payload.get('phone_number')


def test_reading_wallet_details_by_normal_user(test_client, normal_user_payload, db_session, user_payload):
    token = get_token(test_client, normal_user_payload)

    test_client.post('/auth/create', json=user_payload)

    user_id = db_session.query(User).filter(User.email == user_payload.get("email")).first().id

    response = test_client.get(f'/wallets/details?user_id={user_id}', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get("detail") == "You do not have enough permission to read wallets"


def test_reading_wallet_details_with_no_query_params(test_client, user_payload):
    token = get_token(test_client, user_payload)

    response = test_client.get('/wallets/details', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400
    assert response.json().get("detail") == "At least one of user_id, wallet_id, or phone_number must be provided"


def test_reading_wallet_details_with_invalid_user_id(test_client, user_payload):
    token = get_token(test_client, user_payload)

    response = test_client.get('/wallets/details?user_id=100', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json().get("detail") == "User wallet details not found"


def test_reading_blocked_wallet_details(test_client, user_payload, normal_user_payload, db_session):
    token = get_token(test_client, user_payload)

    create_user(test_client, normal_user_payload, token)

    normal_user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    wallet_payload = {
        "user_id": normal_user_id,
        "user_phone_number": normal_user_payload.get('phone_number'),
    }

    test_client.post('/wallets/', headers={"Authorization": f"Bearer {token}"}, json=wallet_payload)

    wallet = db_session.query(Wallet).filter(Wallet.user_id == normal_user_id).first()
    wallet.is_blocked = True
    db_session.commit()


    response = test_client.get(f'/wallets/details?user_id={normal_user_id}',
                               headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json().get("detail") == "Wallet is blocked. Please contact support for more information"


