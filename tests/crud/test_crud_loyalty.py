from fastapi.security import OAuth2PasswordRequestForm

from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user
from app.crud.crud_loyalty import read_all_loyalties, read_user_loyalty, redeem_loyalty_points, MINIMUM_REDEEM_POINTS
from app.crud.crud_transaction import top_wallet, debit_wallet
from app.crud.crud_user import create_user
from app.models.User import User
from app.schemas.LoyaltySchemas import LoyaltyRedeemSchema
from app.schemas.TransactionSchemas import TransactionRequest
from app.schemas.UserSchemas import UserRequest


def creating_user(user_data, db):
    user_request = UserRequest(**user_data)
    return create_new_user(user_request, db)


def authenticating_user(user, db):
    form_data = OAuth2PasswordRequestForm(username=user.get("email"), password=user.get("password"))
    _, response = authenticate_user(form_data, db)
    _, user_info = get_current_user(response.get("access_token"), db)
    return user_info


def test_read_loyalties(db_session, sys_user_payload, normal_user_payload, credit_transaction_payload,
                        debit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token, TransactionRequest(**credit_transaction_payload))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload))

    # read all loyalties
    status_code, response = read_all_loyalties(db_session, token, 10, 0)

    assert status_code == 200
    assert len(response) == 1


def test_read_loyalties_by_normal_user(db_session, sys_user_payload, normal_user_payload, credit_transaction_payload,
                                       debit_transaction_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)

    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # read all loyalties
    status_code, response = read_all_loyalties(db_session, token, 10, 0)

    assert status_code == 401
    assert response.get('message') == "You do not have enough permission to read loyalties"


def test_read_user_loyalty(db_session, sys_user_payload, normal_user_payload, credit_transaction_payload,
                           debit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token, TransactionRequest(**credit_transaction_payload))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload))

    # get user_id
    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    # read user loyalty
    status_code, response = read_user_loyalty(db_session, token, user_id)

    assert status_code == 200
    assert response.get('user_id') == user_id
    assert response.get('points') == 1


def test_read_user_loyalty_by_normal_user(db_session, normal_user_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)

    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # read user loyalty
    status_code, response = read_user_loyalty(db_session, token, 10)

    assert status_code == 401
    assert response.get('message') == "You do not have enough permission to read this loyalty"


def test_read_user_loyalty_of_unknown_user(db_session, sys_user_payload):
    # create normal user
    creating_user(sys_user_payload, db_session)

    # authenticate normal user
    token = authenticating_user(sys_user_payload, db_session)

    # read user loyalty
    status_code, response = read_user_loyalty(db_session, token, 10)

    assert status_code == 404
    assert response.get('message') == "Loyalty not found"


def test_redeem_loyalty_points(db_session, sys_user_payload, normal_user_payload,
                               credit_transaction_payload_for_loyalty,
                               debit_transaction_payload_for_loyalty):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token, TransactionRequest(**credit_transaction_payload_for_loyalty))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload_for_loyalty))

    # get user_id
    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 10
    }

    # redeem loyalty points
    status_code, response = redeem_loyalty_points(db_session, token, LoyaltyRedeemSchema(**redeem_loyalty_request))

    assert status_code == 201
    assert response.get('message') == "Points redeemed successfully. Cash equivalent: $0.1"


def test_redeem_minimum_loyalty_points(db_session, sys_user_payload, normal_user_payload,
                                            credit_transaction_payload,
                                            debit_transaction_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token, TransactionRequest(**credit_transaction_payload))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload))

    # get user_id
    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 10
    }

    # redeem loyalty points
    status_code, response = redeem_loyalty_points(db_session, token, LoyaltyRedeemSchema(**redeem_loyalty_request))

    assert status_code == 400
    assert response.get('message') == f"Minimum points to redeem is {MINIMUM_REDEEM_POINTS}"


def test_redeem_insufficient_loyalty_points(db_session, sys_user_payload, normal_user_payload,
                                            credit_transaction_payload_for_loyalty,
                                            debit_transaction_payload_for_loyalty):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**normal_user_payload), db_session, token)

    # top up wallet
    top_wallet(db_session, token, TransactionRequest(**credit_transaction_payload_for_loyalty))

    # debit wallet
    debit_wallet(db_session, token, TransactionRequest(**debit_transaction_payload_for_loyalty))

    # get user_id
    user_id = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first().id

    redeem_loyalty_request = {
        "user_id": user_id,
        "quantity": 1000
    }

    # redeem loyalty points
    status_code, response = redeem_loyalty_points(db_session, token, LoyaltyRedeemSchema(**redeem_loyalty_request))

    assert status_code == 400
    assert response.get('message') == "Insufficient points to redeem"


def test_redeem_loyalty_points_by_normal_user(db_session, user_payload, normal_user_payload):
    # create normal user
    creating_user(normal_user_payload, db_session)
    # authenticate normal user
    token = authenticating_user(normal_user_payload, db_session)

    # create normal user with wallet
    create_user(UserRequest(**user_payload), db_session, token)

    redeem_loyalty_request = {
        "user_id": 20,
        "quantity": 1000
    }

    # redeem loyalty points
    status_code, response = redeem_loyalty_points(db_session, token, LoyaltyRedeemSchema(**redeem_loyalty_request))

    assert status_code == 401
    assert response.get('message') == "You do not have enough permission to redeem loyalty points"


def test_redeem_loyalty_points_for_unknown_user(db_session, sys_user_payload):
    # create superuser
    creating_user(sys_user_payload, db_session)
    # authenticate superuser
    token = authenticating_user(sys_user_payload, db_session)

    redeem_loyalty_request = {
        "user_id": 20,
        "quantity": 1000
    }

    # redeem loyalty points
    status_code, response = redeem_loyalty_points(db_session, token, LoyaltyRedeemSchema(**redeem_loyalty_request))

    assert status_code == 404
    assert response.get('message') == "Loyalty not found"
