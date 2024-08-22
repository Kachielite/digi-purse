from fastapi.security import OAuth2PasswordRequestForm

from app.crud.crud_auth import authenticate_user, get_current_user, create_new_user
from app.crud.crud_user import get_all_users, create_user, update_user_data, delete_user
from app.models.User import User
from app.schemas.UserRequest import UserRequest
from app.schemas.UserSchemas import UserUpdateRequest


def creating_user(user_data, db):
    user_request = UserRequest(**user_data)
    return create_new_user(user_request, db)


def test_get_all_users(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    token = response.get("access_token")

    _, user = get_current_user(token, db_session)
    status_code, response = get_all_users(db_session, user)

    assert status_code == 200
    assert len(response) == 1


def test_create_user_by_normal_user(db_session, user_payload, sys_user_payload, normal_user_payload):
    creating_user(normal_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=normal_user_payload.get("email"),
                                          password=normal_user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, token = get_current_user(response.get("access_token"), db_session)

    status_code, response = create_user(user_payload, db_session, token)

    assert status_code == 401
    assert response["message"] == "You do not have enough permission to create users"


def test_create_user_with_existing_email(db_session, user_payload, user_payload_existing_email):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, token = get_current_user(response.get("access_token"), db_session)

    user_request_existing_email = UserRequest(**user_payload_existing_email)
    status_code, response = create_user(user_request_existing_email, db_session, token)

    assert status_code == 400
    assert response["message"] == "User with the associated email already exist"


def test_create_user_with_existing_phone_number(db_session, user_payload, user_payload_existing_phone_number):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, token = get_current_user(response.get("access_token"), db_session)

    user_request_existing_phone_number = UserRequest(**user_payload_existing_phone_number)
    status_code, response = create_user(user_request_existing_phone_number, db_session, token)

    assert status_code == 400
    assert response["message"] == "User with the associated phone number already exist"


def test_create_user_with_existing_username(db_session, user_payload, user_payload_existing_username):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, token = get_current_user(response.get("access_token"), db_session)

    user_request_existing_username = UserRequest(**user_payload_existing_username)
    status_code, response = create_user(user_request_existing_username, db_session, token)

    assert status_code == 400
    assert response["message"] == "User with the associated username already exist"


def test_create_user_with_new_user_admin(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, token = get_current_user(response.get("access_token"), db_session)

    user_request = UserRequest(**normal_user_payload)
    status_code, response = create_user(user_request, db_session, token)

    assert status_code == 201
    assert response["message"] == "User created successfully"


def test_update_user_by_normal_user(db_session, normal_user_payload, user_update_payload):
    creating_user(normal_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=normal_user_payload.get("email"),
                                          password=normal_user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    update_request = UserUpdateRequest(**user_update_payload)
    status_code, response = update_user_data(update_request, 1, user, db_session)

    assert status_code == 401
    assert response["message"] == "You do not have enough permission to update users"


def test_update_user_by_non_existing_user(db_session, user_payload, normal_user_payload, user_update_payload):
    creating_user(user_payload, db_session)
    creating_user(normal_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"),
                                          password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    user_to_be_updated = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first()

    update_request = UserUpdateRequest(**user_update_payload)
    status_code, response = update_user_data(update_request, user_to_be_updated.id, user, db_session)

    assert status_code == 200
    assert response["message"] == "User role updated successfully"


def test_delete_user_non_existing_user(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"),
                                          password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    status_code, response = delete_user(user, db_session, 10)

    assert status_code == 404
    assert response["message"] == "User not found"


def test_delete_user_by_normal_user(db_session, normal_user_payload, user_payload):
    creating_user(normal_user_payload, db_session)
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=normal_user_payload.get("email"),
                                          password=normal_user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    user_to_be_deleted = db_session.query(User).filter(User.email == user_payload.get("email")).first()
    status_code, response = delete_user(user, db_session, user_to_be_deleted.id)

    assert status_code == 401
    assert response["message"] == "You do not have enough permission to delete users"


def test_delete_admin_user_admin_user(db_session, user_payload, admin_user_payload):
    creating_user(user_payload, db_session)
    creating_user(admin_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"),
                                          password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    user_to_be_deleted = db_session.query(User).filter(User.email == admin_user_payload.get("email")).first()
    status_code, response = delete_user(user, db_session, user_to_be_deleted.id)

    assert status_code == 401
    assert response["message"] == "Only Sys admin can delete Admin users"


def test_delete_sys_user_admin_user(db_session, user_payload, sys_user_payload):
    creating_user(user_payload, db_session)
    creating_user(sys_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"),
                                          password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    user_to_be_deleted = db_session.query(User).filter(User.email == sys_user_payload.get("email")).first()
    status_code, response = delete_user(user, db_session, user_to_be_deleted.id)

    assert status_code == 401
    assert response["message"] == "Only Sys admin can delete a Sys admin user"


def test_delete_user(db_session, user_payload, normal_user_payload):
    creating_user(user_payload, db_session)
    creating_user(normal_user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"),
                                          password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    _, user = get_current_user(response.get("access_token"), db_session)

    user_to_be_deleted = db_session.query(User).filter(User.email == normal_user_payload.get("email")).first()
    status_code, response = delete_user(user, db_session, user_to_be_deleted.id)

    assert status_code == 200
    assert response["message"] == "User deleted successfully"
