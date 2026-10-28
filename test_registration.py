import pytest
from dotenv import load_dotenv

load_dotenv()

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def get_csrf_token(client):
    response = client.get("/register")
    assert response.status_code == 200

    with client.session_transaction() as session:
        return session["registration_csrf_token"]


def test_registration_rejects_short_password(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "username": "valid_test_user",
            "email": "test@example.com",
            "password": "short",
            "confirm_password": "short",
        },
    )

    assert response.status_code == 400
    assert b"12" in response.data


def test_registration_rejects_mismatched_passwords(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "username": "mismatch_test_user",
            "email": "mismatch@example.com",
            "password": "A-Strong-Test-Password-123",
            "confirm_password": "A-Different-Test-Password-456",
        },
    )

    assert response.status_code == 400
    assert b"passwords do not match" in response.data.lower()


def test_registration_rejects_invalid_csrf_token(client):
    response = client.post(
        "/register",
        data={
            "csrf_token": "invalid-token",
            "username": "csrf_test_user",
            "email": "csrf@example.com",
            "password": "A-Strong-Test-Password-123",
            "confirm_password": "A-Strong-Test-Password-123",
        },
    )

    assert response.status_code == 400
    assert b"session expired" in response.data.lower()


def test_registration_rejects_duplicate_username(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "username": "TSUKUYOMI_TEST",
            "email": "another_test@example.com",
            "password": "A-Strong-Test-Password-123",
            "confirm_password": "A-Strong-Test-Password-123",
        },
    )

    assert response.status_code == 409
    assert b"already registered" in response.data.lower()


def test_registration_rejects_duplicate_email(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "username": "another_test_user",
            "email": "TSUKUYOMI_TEST@example.com",
            "password": "A-Strong-Test-Password-123",
            "confirm_password": "A-Strong-Test-Password-123",
        },
    )

    assert response.status_code == 409
    assert b"already registered" in response.data.lower()


def test_registration_rejects_invalid_username(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/register",
        data={
            "csrf_token": csrf_token,
            "username": "invalid user!",
            "email": "invalid_username@example.com",
            "password": "A-Strong-Test-Password-123",
            "confirm_password": "A-Strong-Test-Password-123",
        },
    )

    assert response.status_code == 400
    assert b"letters, numbers, or underscores" in response.data.lower()
