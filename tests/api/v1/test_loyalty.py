from app.crud.crud_loyalty import MINIMUM_REDEEM_POINTS
from app.models.User import User


def get_token(client, user):
    client.post('/auth/create', json=user)
    response = client.post('/auth/token',
                           data={"username": user.get('email'), "password": user.get('password')})

    return response.json().get('access_token')


def create_user(client, user, token):
    return client.post('/users/add', headers={"Authorization": f"Bearer {token}"}, json=user)


def test_read_loyalties(test_client, db_session, sys_user_payload, normal_user_payload, credit_transaction_payload,
                        debit_transaction_payload):
    token = get_token(test_client, sys_user_payload)

    create_user(test_client, normal_user_payload, token)

    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=credit_transaction_payload)

    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=debit_transaction_payload)

    response = test_client.get('/loyalty/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_loyalties_by_normal_user(test_client, db_session, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    response = test_client.get('/loyalty/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get('detail') == "You do not have enough permission to read loyalties"


def test_read_loyalty(test_client, db_session, sys_user_payload, normal_user_payload, credit_transaction_payload,
                      debit_transaction_payload):
    token = get_token(test_client, sys_user_payload)

    create_user(test_client, normal_user_payload, token)

    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=credit_transaction_payload)

    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=debit_transaction_payload)

    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    response = test_client.get(f'/loyalty/{user_id}', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json().get('user_id') == user_id
    assert response.json().get('points') == 1


def test_read_loyalty_by_normal_user(test_client, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    response = test_client.get('/loyalty/20', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json().get('detail') == "You do not have enough permission to read this loyalty"


def test_read_loyalty_for_unknown_user(test_client, sys_user_payload):
    token = get_token(test_client, sys_user_payload)

    response = test_client.get('/loyalty/20', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json().get('detail') == "Loyalty not found"


def test_redeem_loyalty_points(test_client, db_session, sys_user_payload, normal_user_payload,
                               credit_transaction_payload_for_loyalty,
                               debit_transaction_payload_for_loyalty):
    token = get_token(test_client, sys_user_payload)

    create_user(test_client, normal_user_payload, token)

    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=credit_transaction_payload_for_loyalty)

    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=debit_transaction_payload_for_loyalty)

    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 10
    }

    response = test_client.post('/loyalty/redeem', headers={"Authorization": f"Bearer {token}"},
                                json=redeem_loyalty_request)

    assert response.status_code == 201
    assert response.json().get('message') == "Points redeemed successfully. Cash equivalent: $0.1"


def test_redeem_minimum_loyalty_points(test_client, db_session, sys_user_payload, normal_user_payload,
                                       credit_transaction_payload,
                                       debit_transaction_payload):
    token = get_token(test_client, sys_user_payload)

    create_user(test_client, normal_user_payload, token)

    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=credit_transaction_payload)

    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=debit_transaction_payload)

    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 10
    }

    response = test_client.post('/loyalty/redeem', headers={"Authorization": f"Bearer {token}"},
                                json=redeem_loyalty_request)

    assert response.status_code == 400
    assert response.json().get('detail') == f"Minimum points to redeem is {MINIMUM_REDEEM_POINTS}"


def test_redeem_insufficient_loyalty_points(test_client, db_session, sys_user_payload, normal_user_payload,
                                            credit_transaction_payload_for_loyalty,
                                            debit_transaction_payload_for_loyalty):
    token = get_token(test_client, sys_user_payload)

    create_user(test_client, normal_user_payload, token)

    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=credit_transaction_payload_for_loyalty)

    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                     json=debit_transaction_payload_for_loyalty)

    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 1000
    }

    response = test_client.post('/loyalty/redeem', headers={"Authorization": f"Bearer {token}"},
                                json=redeem_loyalty_request)

    assert response.status_code == 400
    assert response.json().get('detail') == "Insufficient points to redeem"


def test_redeem_loyalty_points_by_normal_user(test_client, normal_user_payload):
    token = get_token(test_client, normal_user_payload)

    redeem_loyalty_request = {
        "user_id": 20,
        "quantity": 10
    }

    response = test_client.post('/loyalty/redeem', headers={"Authorization": f"Bearer {token}"},
                                json=redeem_loyalty_request)

    assert response.status_code == 401
    assert response.json().get('detail') == "You do not have enough permission to redeem loyalty points"


def test_redeem_loyalty_points_for_unknown_user(test_client, sys_user_payload):
    token = get_token(test_client, sys_user_payload)

    redeem_loyalty_request = {
        "user_id": 20,
        "quantity": 10
    }

    response = test_client.post('/loyalty/redeem', headers={"Authorization": f"Bearer {token}"},
                                json=redeem_loyalty_request)

    assert response.status_code == 404
    assert response.json().get('detail') == "Loyalty not found"
