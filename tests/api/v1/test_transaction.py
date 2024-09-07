from app.models.Transaction import Transaction
from app.models.User import User
from app.models.Wallet import Wallet
from app.schemas.WalletSchemas import WalletCreationRequest


def get_token(client, user):
    client.post('/auth/create', json=user)
    response = client.post('/auth/token',
                           data={"username": user.get('email'), "password": user.get('password')})

    return response.json().get('access_token')


def create_user(client, user, token):
    return client.post('/users/add', headers={"Authorization": f"Bearer {token}"}, json=user)


def test_top_wallet(test_client, db_session, sys_user_payload, normal_user_payload, credit_transaction_payload):
    # create superuser & authenticate superuser
    token = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token}"}, json=normal_user_payload)

    # top up wallet
    response = test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                                json=credit_transaction_payload)

    assert response.status_code == 201
    assert response.json().get('message') == "Wallet topped up successfully"


def test_top_up_by_normal_user(test_client, db_session, sys_user_payload, normal_user_payload, user_payload,
                               credit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create & authenticate normal user
    token_normal_user = get_token(test_client, normal_user_payload)

    # create user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=user_payload)

    # top wallet by normal user
    response = test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token_normal_user}"},
                                json=credit_transaction_payload)

    assert response.status_code == 403
    assert response.json().get('detail') == "Unauthorized access"


def test_top_up_non_existing_wallet(test_client, db_session, sys_user_payload, credit_transaction_payload):
    # create superuser & authenticate superuser
    token = get_token(test_client, sys_user_payload)

    # top wallet by normal user
    response = test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token}"},
                                json=credit_transaction_payload)

    assert response.status_code == 404
    assert response.json().get('detail') == "Wallet not found"


def test_debit_wallet_by_normal_user(test_client, db_session, sys_user_payload, normal_user_payload, user_payload,
                                     debit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create & authenticate normal user
    token_normal_user = get_token(test_client, normal_user_payload)

    # create user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=user_payload)

    # top wallet by normal user
    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_normal_user}"},
                                json=debit_transaction_payload)

    assert response.status_code == 403
    assert response.json().get('detail') == "Unauthorized access"


def test_debit_non_existing_wallet(test_client, db_session, sys_user_payload, debit_transaction_payload):
    # create superuser & authenticate superuser
    token = get_token(test_client, sys_user_payload)

    # top wallet by normal user
    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token}"},
                                json=debit_transaction_payload)

    assert response.status_code == 404
    assert response.json().get('detail') == "Wallet not found"


def test_debiting_blocked_wallet(test_client, db_session, sys_user_payload, normal_user_payload,
                                 debit_transaction_payload,
                                 credit_transaction_payload, block_wallet_request):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=normal_user_payload, )

    # top wallet by normal user
    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=credit_transaction_payload)

    # block normal user wallet
    wallet = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload.get('phone_number')).first()
    wallet.is_blocked = True
    db_session.commit()

    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                                json=debit_transaction_payload)

    assert response.status_code == 403
    assert response.json().get('detail') == "Wallet is blocked"


def test_debiting_insufficient_fund_wallet(test_client, db_session, sys_user_payload, normal_user_payload,
                                           debit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=normal_user_payload, )

    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                                json=debit_transaction_payload)

    assert response.status_code == 400
    assert response.json().get('detail') == "Insufficient balance"


def test_debiting_self_wallet(test_client, db_session, sys_user_payload, sys_user_debit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # Get superuser id
    system_user_id = db_session.query(User).filter(User.email == sys_user_payload.get('email')).first().id

    wallet_creation_request = {
        "user_id": system_user_id,
        "user_phone_number": sys_user_payload.get('phone_number')
    }

    # create wallet for superuser
    test_client.post('/wallets', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=wallet_creation_request, )

    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                                json=sys_user_debit_transaction_payload)

    assert response.status_code == 400
    assert response.json().get('detail') == "You cannot debit your own wallet"


def test_debiting_wallet(test_client, db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                         credit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=normal_user_payload, )

    # top wallet by normal user
    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=credit_transaction_payload)

    # debit wallet
    response = test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                                json=debit_transaction_payload)

    assert response.status_code == 201
    assert response.json().get('message') == "Wallet debited successfully"


def test_get_all_transaction_history(test_client, db_session, sys_user_payload, normal_user_payload,
                                     debit_transaction_payload,
                                     credit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=normal_user_payload, )

    # top wallet by normal user
    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=credit_transaction_payload)

    # debit wallet
    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=debit_transaction_payload)

    response = test_client.get('/transactions', headers={"Authorization": f"Bearer {token_super_user}"})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_transactions_history(test_client, db_session, sys_user_payload, normal_user_payload,
                                       debit_transaction_payload,
                                       credit_transaction_payload):
    # create superuser & authenticate superuser
    token_super_user = get_token(test_client, sys_user_payload)

    # create normal user
    test_client.post('/users/add', headers={"Authorization": f"Bearer {token_super_user}"}, json=normal_user_payload, )

    # top wallet by normal user
    test_client.post('/transactions/top-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=credit_transaction_payload)

    # debit wallet
    test_client.post('/transactions/debit-wallet', headers={"Authorization": f"Bearer {token_super_user}"},
                     json=debit_transaction_payload)

    # Get normal user id
    normal_user_id = (
        db_session.query(User).filter(User.phone_number == normal_user_payload.get('phone_number')).first()
        .id)

    response = test_client.get(f'/transactions/user/{normal_user_id}',
                               headers={"Authorization": f"Bearer {token_super_user}"})

    assert response.status_code == 200
    assert len(response.json()) == 2


