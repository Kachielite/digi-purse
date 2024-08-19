import pytest

from app.core.security import encrypt_password, validate_password, create_token, SECRET_KEY, decode_token


# Test password encryption
def test_password_encryption():
    password = "test_password"
    hash_password = encrypt_password(password)

    assert validate_password(password, hash_password) is True
    assert validate_password("wrong_password", hash_password) is False


# Test token creation and decoding
def test_token_creation_and_decoding():
    user = "test user"
    user_id = 1
    role = "ADMIN"

    token = create_token(user, user_id, role)

    decoded_token = decode_token(token)

    assert decoded_token.get("username") == user
    assert decoded_token.get("user_id") == user_id
    assert decoded_token.get("role") == role


# Test decode_token with an invalid token
def test_invalid_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token("invalid_token")