from fastapi.security import OAuth2PasswordRequestForm

from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user
from app.crud.crud_transaction import top_wallet, debit_wallet, transaction_all_history, transaction_user_history, \
    transaction_by_id
from app.crud.crud_user import create_user
from app.crud.crud_wallet import block_user_wallet, create_wallet
from app.models.Transaction import Transaction
from app.models.User import User
from app.models.Wallet import Wallet
from app.schemas.TransactionSchemas import TransactionRequest
from app.schemas.UserSchemas import UserRequest
from app.schemas.WalletSchemas import WalletUpdateRequest, WalletCreationRequest


def creating_user(user_data, db):
    user_request = UserRequest(**user_data)
    return create_new_user(user_request, db)


def authenticating_user(user, db):
    form_data = OAuth2PasswordRequestForm(username=user.get("email"), password=user.get("password"))
    _, response = authenticate_user(form_data, db)
    _, user_info = get_current_user(response.get("access_token"), db)
    return user_info


def test_top_wallet(db_session, sys_user_payload, normal_user_payload, credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    super_user_info = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, super_user_info)

    # top up wallet
    status_code, response = top_wallet(db_session, super_user_info, TransactionRequest(**credit_transaction_payload))

    assert status_code == 200
    assert response["message"] == "Wallet topped up successfully"


def test_top_by_normal_user(db_session, normal_user_payload, user_payload, credit_transaction_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)
    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # create user with wallet
    create_user(UserRequest(**user_payload), db_session, token)

    # top up wallet
    status_code, response = top_wallet(db_session, token,
                                       TransactionRequest(**credit_transaction_payload))

    assert status_code == 403
    assert response["message"] == "Unauthorized access"


def test_top_up_non_existing_wallet(db_session, normal_user_payload, user_payload, credit_transaction_payload):
    # create user
    creating_user(user_payload, db_session)
    # authenticate  user
    token = authenticating_user(user_payload, db_session)

    # top up wallet
    status_code, response = top_wallet(db_session, token,
                                       TransactionRequest(**credit_transaction_payload))

    assert status_code == 404
    assert response["message"] == "Wallet not found"


def test_debit_wallet_by_normal_user(db_session, normal_user_payload, user_payload, debit_transaction_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)
    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # create user with wallet
    create_user(UserRequest(**user_payload), db_session, token)

    # top up wallet
    status_code, response = debit_wallet(db_session, token,
                                         TransactionRequest(**debit_transaction_payload))

    assert status_code == 403
    assert response["message"] == "Unauthorized access"


def test_debit_non_existing_wallet(db_session, normal_user_payload, user_payload, debit_transaction_payload):
    # create user
    creating_user(user_payload, db_session)
    # authenticate  user
    token = authenticating_user(user_payload, db_session)

    # debit wallet
    status_code, response = top_wallet(db_session, token,
                                       TransactionRequest(**debit_transaction_payload))

    assert status_code == 404
    assert response["message"] == "Wallet not found"


def test_debiting_blocked_wallet(db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                                 credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token,
               TransactionRequest(**credit_transaction_payload))

    # block wallet
    db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).update({"is_blocked": True})
    db_session.commit()

    # debit wallet
    status_code, response = debit_wallet(db_session, token,
                                         TransactionRequest(**debit_transaction_payload))

    assert status_code == 403
    assert response["message"] == "Wallet is blocked"


def test_debiting_insufficient_fund_wallet(db_session, sys_user_payload, normal_user_payload,
                                           debit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # debit wallet
    status_code, response = debit_wallet(db_session, token,
                                         TransactionRequest(**debit_transaction_payload))

    assert status_code == 400
    assert response["message"] == "Insufficient balance"


def test_debiting_self_wallet(db_session, sys_user_payload, sys_user_debit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create  superuser with wallet
    system_user_id = db_session.query(User).filter(User.username == sys_user_payload.get('username')).first().id

    wallet_creation_request = WalletCreationRequest(
        user_id=system_user_id,
        user_phone_number=sys_user_payload.get('phone_number')
    )
    create_wallet(db_session, token, wallet_creation_request)

    # debit wallet
    status_code, response = debit_wallet(db_session, token,
                                         TransactionRequest(**sys_user_debit_transaction_payload))

    assert status_code == 400
    assert response["message"] == "You cannot debit your own wallet"


def test_debiting_wallet(db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                         credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token,
               TransactionRequest(**credit_transaction_payload))

    # debit wallet
    status_code, response = debit_wallet(db_session, token,
                                         TransactionRequest(**debit_transaction_payload))

    assert status_code == 200
    assert response["message"] == "Wallet debited successfully"


def test_get_all_transaction_history(db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                                     credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token,
               TransactionRequest(**credit_transaction_payload))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload))

    # get transaction history
    status_code, response = transaction_all_history(db_session, token)

    assert status_code == 200
    assert len(response) == 2


def test_get_all_transaction_history_by_normal_user(db_session, normal_user_payload, debit_transaction_payload,
                                                    credit_transaction_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)
    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # get transaction history
    status_code, response = transaction_all_history(db_session, token)

    assert status_code == 403
    assert response.get('message') == "Unauthorized access"


def test_get_user_transactions_history(db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                                       credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token,
               TransactionRequest(**credit_transaction_payload))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload))

    # user id
    user_id = db_session.query(User).filter(User.username == normal_user_payload.get('username')).first().id

    # get transaction history
    status_code, response = transaction_user_history(db_session, token, user_id)

    assert status_code == 200
    assert len(response) == 2


def test_get_user_transactions_history_by_normal_user(db_session, sys_user_payload, normal_user_payload,
                                                      debit_transaction_payload,
                                                      credit_transaction_payload):
    # create superuser
    creating_user(normal_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(normal_user_payload, db_session)

    # get transaction history
    status_code, response = transaction_user_history(db_session, token, 1)

    assert status_code == 403
    assert response.get('message') == "Unauthorized access"


def test_get_transaction_history_by_id(db_session, sys_user_payload, normal_user_payload, debit_transaction_payload,
                                       credit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token,
               TransactionRequest(**credit_transaction_payload))

    # user id
    user_id = db_session.query(User).filter(User.username == normal_user_payload.get('username')).first().id

    # user wallet id
    user_wallet_id = db_session.query(Wallet).filter(Wallet.user_id == user_id).first().id

    # transaction id
    transaction_id = db_session.query(Transaction).filter(Transaction.wallet_id == user_wallet_id).all()[0].id

    # get transaction history
    status_code, response = transaction_by_id(db_session, token, transaction_id)

    assert status_code == 200
    assert response.get('id') == str(transaction_id)
