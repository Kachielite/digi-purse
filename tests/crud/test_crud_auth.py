from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_token
from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user
from app.models.User import User
from app.schemas.UserSchemas import UserRequest


def creating_user(user_data, db):
    user_request = UserRequest(**user_data)
    return create_new_user(user_request, db)


def test_creating_new_user(db_session, user_payload):
    status_code, response = creating_user(user_payload, db_session)

    assert status_code == 201
    assert response["message"] == "User created successfully"

    new_user = db_session.query(User).filter(User.username == user_payload["username"]).first()
    assert new_user is not None
    assert new_user.username == user_payload["username"]


def test_authenticate_user(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get('email'), password=user_payload.get('password'))
    status_code, response = authenticate_user(form_data, db_session)

    assert status_code == 200
    assert "access_token" in response


def test_unknown_authenticate_user(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username="wrong_username", password="wrong_password")
    status_code, response = authenticate_user(form_data, db_session)

    assert status_code == 404
    assert response.get("message") == "User not found"


def test_wrong_authenticate_user(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password="wrong_password")
    status_code, response = authenticate_user(form_data, db_session)

    assert status_code == 401
    assert response.get("message") == "Wrong Credentials"


def test_get_current_user(db_session, user_payload):
    creating_user(user_payload, db_session)

    form_data = OAuth2PasswordRequestForm(username=user_payload.get("email"), password=user_payload.get("password"))
    _, response = authenticate_user(form_data, db_session)

    token = response.get("access_token")
    status_code, response = get_current_user(token, db_session)

    assert status_code == 200
    assert user_payload.get("username") == response.get("username")


def test_get_current_user_invalid_token(db_session, user_payload):
    invalid_token = create_token("test@mail.com", 1, "ADMIN")
    status_code, response = get_current_user(invalid_token, db_session)

    assert status_code != 200
    assert response.get("message") == "Invalid token"
