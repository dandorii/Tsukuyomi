import pytest
from dotenv import load_dotenv
from argon2 import PasswordHasher
from unittest.mock import patch

load_dotenv()

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def get_login_csrf_token(client):
    response = client.get("/login")
    assert response.status_code == 200

    with client.session_transaction() as session:
        return session["login_csrf_token"]



def test_login_rejects_incorrect_password(client):
    csrf_token = get_login_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "identifier": "tsukuyomi_test",
            "password": "Definitely-Wrong-Password-999",
        },
    )

    assert response.status_code == 401
    assert b"invalid username/email or password" in response.data.lower()

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_rejects_unknown_account(client):
    csrf_token = get_login_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "identifier": "unknown_user_98765",
            "password": "Some-Strong-Password-123",
        },
    )

    assert response.status_code == 401
    assert b"invalid username/email or password" in response.data.lower()

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_rejects_invalid_csrf_token(client):
    response = client.post(
        "/login",
        data={
            "csrf_token": "invalid-csrf-token",
            "identifier": "tsukuyomi_test",
            "password": "Some-Strong-Password-123",
        },
    )

    assert response.status_code == 400
    assert b"session expired" in response.data.lower()

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_succeeds_and_redirects_to_account(client):
    password = "Test-Password-123!"
    password_hash = PasswordHasher().hash(password)

    fake_user = {
        "id": 987654,
        "username": "login_test_user",
        "email": "login_test@example.com",
        "password_hash": password_hash,
    }

    csrf_token = get_login_csrf_token(client)

    with patch(
        "app.get_user_by_username_or_email",
        return_value=fake_user,
    ):
        response = client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "login_test_user",
                "password": password,
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/account")

    with client.session_transaction() as session:
        assert session["user_id"] == 987654
        assert session["username"] == "login_test_user"
        assert "visitor_id" not in session or session["visitor_id"]


def test_account_redirects_unauthenticated_visitor(client):
    response = client.get("/account")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_logout_rejects_invalid_csrf_token(client):
    with client.session_transaction() as session:
        session["user_id"] = 987654
        session["username"] = "login_test_user"
        session["logout_csrf_token"] = "valid-token"

    response = client.post(
        "/logout",
        data={"csrf_token": "invalid-token"},
    )

    assert response.status_code == 400
    assert b"Invalid CSRF token." in response.data

    with client.session_transaction() as session:
        assert session["user_id"] == 987654
        assert session["username"] == "login_test_user"


def test_logout_succeeds_and_clears_session(client):
    with client.session_transaction() as session:
        session["user_id"] = 987654
        session["username"] = "login_test_user"
        session["visitor_id"] = "visitor-test-123"
        session["logout_csrf_token"] = "valid-logout-token"

    response = client.post(
        "/logout",
        data={"csrf_token": "valid-logout-token"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "username" not in session
        assert "logout_csrf_token" not in session
        assert "visitor_id" not in session