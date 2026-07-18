from app.services.auth_service import AuthService


def test_password_hashing_and_verification():
    service = AuthService()
    password = "StrongPass123!"

    hashed = service.hash_password(password)

    assert hashed != password
    assert service.verify_password(password, hashed) is True
    assert service.verify_password("wrong-password", hashed) is False


def test_token_generation_and_decoding():
    service = AuthService()
    payload = {"sub": "user-123", "role": "USER"}

    access_token = service.create_access_token(payload)
    refresh_token = service.create_refresh_token(payload)

    assert access_token
    assert refresh_token

    decoded_access = service.decode_token(access_token)
    decoded_refresh = service.decode_token(refresh_token)

    assert decoded_access["sub"] == "user-123"
    assert decoded_refresh["sub"] == "user-123"
    assert decoded_access["role"] == "USER"
    assert decoded_refresh["role"] == "USER"
