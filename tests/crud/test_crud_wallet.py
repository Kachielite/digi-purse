import uuid

from fastapi.security import OAuth2PasswordRequestForm

from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user
from app.crud.crud_user import create_user
from app.crud.crud_wallet import create_wallet, read_all_wallet, read_wallet_details, block_user_wallet, \
    delete_user_wallet
from app.models.User import User
from app.models.Wallet import Wallet
from app.schemas.UserSchemas import UserRequest
from app.schemas.WalletSchemas import WalletCreationRequest, WalletUpdateRequest


def creating_user(user_data, db):
    user_request = UserRequest(**user_data)
    return create_new_user(user_request, db)


def authenticating_user(user, db):
    form_data = OAuth2PasswordRequestForm(username=user.get("email"), password=user.get("password"))
    _, response = authenticate_user(form_data, db)
    _, user_info = get_current_user(response.get("access_token"), db)
    return user_info


def test_creating_wallet(db_session, user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    new_user = db_session.query(User).filter(User.username == user_payload["username"]).first()

    new_wallet = WalletCreationRequest(
        user_id=new_user.id,
        user_phone_number=user_payload["phone_number"]
    )

    code, response = create_wallet(db_session, user_info, new_wallet)

    assert code == 201
    assert response["message"] == "Wallet created successfully"


def test_creating_wallet_for_existing_wallet(db_session, user_payload, normal_user_payload):
    # Create admin user and authenticate user
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    # Create normal user which should create a wallet at the same time
    user_request = UserRequest(**normal_user_payload)
    create_user(user_request, db_session, user_info)
    normal_user = db_session.query(User).filter(User.email == normal_user_payload["email"]).first()

    # Check if the wallet already exists by directly creating a wallet for the same normal user
    new_wallet = WalletCreationRequest(
        user_id=normal_user.id,
        user_phone_number=normal_user.phone_number
    )

    code, response = create_wallet(db_session, user_info, new_wallet)

    assert code == 400
    assert response["message"] == "User already has a wallet"


def test_creating_wallet_by_normal_user(db_session, user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)
    user_info = authenticating_user(normal_user_payload, db_session)

    new_wallet = WalletCreationRequest(
        user_id=10,
        user_phone_number="234789124"
    )

    code, response = create_wallet(db_session, user_info, new_wallet)

    assert code == 401
    assert response["message"] == "You do not have enough permission to create wallets"


def test_reading_all_wallet(db_session, user_payload, normal_user_payload, admin_user_payload, sys_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    admin_user_payload = UserRequest(**admin_user_payload)
    sys_user_payload = UserRequest(**sys_user_payload)

    create_user(normal_user_request, db_session, user_info)
    create_user(admin_user_payload, db_session, user_info)
    create_user(sys_user_payload, db_session, user_info)

    code, response = read_all_wallet(db_session, user_info)

    assert code == 200
    assert len(response) == 3


def test_reading_all_wallet_by_normal_user(db_session, user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)
    user_info = authenticating_user(normal_user_payload, db_session)

    code, response = read_all_wallet(db_session, user_info)

    assert code == 401
    assert response["message"] == "You do not have enough permission to read wallets"


def test_reading_wallet_details(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    code, response = read_wallet_details(db_session, user_info, None, None, normal_user_payload.get("phone_number"))

    assert code == 200
    assert response["user_phone_number"] == normal_user_payload.get("phone_number")


def test_reading_wallet_details_by_normal_user(db_session, user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)
    user_info = authenticating_user(normal_user_payload, db_session)

    user_request = UserRequest(**user_payload)
    create_user(user_request, db_session, user_info)

    code, response = read_wallet_details(db_session, user_info, None, None, user_payload.get("phone_number"))

    assert code == 401
    assert response["message"] == "You do not have enough permission to read wallets"


def test_reading_wallet_details_with_no_query(db_session, user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    code, response = read_wallet_details(db_session, user_info, None, None, None)

    assert code == 400
    assert response["message"] == "At least one of user_id, wallet_id, or phone_number must be provided"


def test_reading_wallet_details_with_invalid_query(db_session, user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    code, response = read_wallet_details(db_session, user_info, 10, None, None)

    assert code == 404
    assert response["message"] == "User wallet details not found"


def test_reading_blocked_wallet_details(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    normal_user_wallet_id = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).first().id

    db_session.query(Wallet).filter(Wallet.id == normal_user_wallet_id).update({"is_blocked": True})
    db_session.commit()

    code, response = read_wallet_details(db_session, user_info, None, None, normal_user_payload.get("phone_number"))

    assert code == 403
    assert response["message"] == "Wallet is blocked. Please contact support for more information"


def test_block_wallet(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    normal_user_wallet_id = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).first().id

    block_request = WalletUpdateRequest(is_blocked=True)

    code, response = block_user_wallet(user_info, db_session, normal_user_wallet_id, block_request)

    assert code == 200
    assert response["message"] == "Wallet blocked successfully"


def test_unblock_wallet(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    normal_user_wallet_id = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).first().id

    db_session.query(Wallet).filter(Wallet.id == normal_user_wallet_id).update({"is_blocked": True})
    db_session.commit()

    block_request = WalletUpdateRequest(is_blocked=False)

    code, response = block_user_wallet(user_info, db_session, normal_user_wallet_id, block_request)

    assert code == 200
    assert response["message"] == "Wallet unblocked successfully"


def test_blocking_already_blocked_wallet(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    normal_user_wallet_id = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).first().id

    db_session.query(Wallet).filter(Wallet.id == normal_user_wallet_id).update({"is_blocked": True})
    db_session.commit()

    block_request = WalletUpdateRequest(is_blocked=True)

    code, response = block_user_wallet(user_info, db_session, normal_user_wallet_id, block_request)

    assert code == 400
    assert response["message"] == "Wallet is already blocked"


def test_blocking_wallet_by_normal_user(db_session, user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)
    user_info = authenticating_user(normal_user_payload, db_session)

    block_request = WalletUpdateRequest(is_blocked=True)

    code, response = block_user_wallet(user_info, db_session, str(uuid.uuid4()), block_request)

    assert code == 401
    assert response["message"] == "You do not have enough permission to block wallets"


def test_deleting_wallet(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    user_info = authenticating_user(user_payload, db_session)

    normal_user_request = UserRequest(**normal_user_payload)
    create_user(normal_user_request, db_session, user_info)

    normal_user_wallet_id = db_session.query(Wallet).filter(
        Wallet.user_phone_number == normal_user_payload["phone_number"]).first().id

    code, response = delete_user_wallet(db_session, user_info,  normal_user_wallet_id)

    assert code == 200
    assert response["message"] == "Wallet deleted successfully"


def test_deleting_wallet_by_normal_user(db_session, user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)
    user_info = authenticating_user(normal_user_payload, db_session)

    code, response = delete_user_wallet(db_session, user_info, str(uuid.uuid4()))

    assert code == 401
    assert response["message"] == "You do not have enough permission to delete wallets"


