from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing_works():
    password_hash = get_password_hash("test-password")

    assert password_hash != "test-password"


def test_password_verification_works():
    password_hash = get_password_hash("test-password")

    assert verify_password("test-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_jwt_token_creation_works():
    token = create_access_token({"sub": "surya"})

    assert isinstance(token, str)
    assert token


def test_jwt_decoding_works():
    token = create_access_token({"sub": "surya"})
    payload = decode_access_token(token)

    assert payload["sub"] == "surya"
