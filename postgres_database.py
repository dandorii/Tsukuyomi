import os
import secrets
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timezone


def get_connection():
    """Open a connection to the new PostgreSQL database."""
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg.connect(
        database_url,
        connect_timeout=10,
        row_factory=dict_row,
    )


def initialize_database():
    """Create the new private-letter table if it doesn't exist."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS letters (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                owner_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                recipient TEXT NOT NULL DEFAULT '',
                body TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sealed BOOLEAN NOT NULL DEFAULT FALSE,
                published BOOLEAN NOT NULL DEFAULT FALSE,
                share_token TEXT UNIQUE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_letters_owner_updated
            ON letters (owner_id, updated_at DESC)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username VARCHAR(30) NOT NULL UNIQUE,
                email VARCHAR(254) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower
            ON users (LOWER(username))
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
            ON users (LOWER(email))
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_letter(owner_id, title="", recipient="", body=""):
    """Save a new private letter for its anonymous owner."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            INSERT INTO letters (owner_id, title, recipient, body)
            VALUES (%s, %s, %s, %s)
            RETURNING id, owner_id, title, recipient, body,
                      created_at, updated_at, sealed, published, share_token
            """,
            (owner_id, title, recipient, body),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_letters_by_owner(owner_id):
    """Return only letters belonging to the specified owner."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, owner_id, title, recipient, body,
                   created_at, updated_at, sealed, published, share_token
            FROM letters
            WHERE owner_id = %s
            ORDER BY updated_at DESC, id DESC
            """,
            (owner_id,),
        ).fetchall()

    finally:
        connection.close()


def get_letter_by_owner(owner_id, letter_id):
    """Return one letter only if it belongs to the specified owner."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, owner_id, title, recipient, body,
                   created_at, updated_at, sealed, published, share_token
            FROM letters
            WHERE id = %s
              AND owner_id = %s
            """,
            (letter_id, owner_id),
        ).fetchone()

    finally:
        connection.close()


def update_letter(owner_id, letter_id, title, recipient, body):
    """Update a letter only if it belongs to the specified owner."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            UPDATE letters
            SET title = %s,
                recipient = %s,
                body = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND sealed = FALSE
            RETURNING id, owner_id, title, recipient, body,
                      created_at, updated_at, sealed, published, share_token
            """,
            (title, recipient, body, letter_id, owner_id),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_letter(owner_id, letter_id):
    """Delete a letter only if it belongs to the owner and is unsealed."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            DELETE FROM letters
            WHERE id = %s
              AND owner_id = %s
              AND sealed = FALSE
            RETURNING id
            """,
            (letter_id, owner_id),
        ).fetchone()

        connection.commit()
        return row is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def seal_letter(owner_id, letter_id):
    """Seal a letter only if it belongs to the owner and is not already sealed."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            UPDATE letters
            SET sealed = TRUE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND sealed = FALSE
            RETURNING id, owner_id, title, recipient, body,
                      created_at, updated_at, sealed, published, share_token
            """,
            (letter_id, owner_id),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def publish_letter(owner_id, letter_id):
    """Publish an owner's letter using a random share token."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        share_token = secrets.token_urlsafe(32)

        row = connection.execute(
            """
            UPDATE letters
            SET published = TRUE,
                share_token = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND published = FALSE
            RETURNING id, owner_id, title, recipient, body,
                      created_at, updated_at, sealed, published, share_token
            """,
            (share_token, letter_id, owner_id),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_published_letter(share_token):
    """Return a letter only when its share token is valid and published."""
    if not share_token:
        return None

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, title, recipient, body, created_at, updated_at, sealed
            FROM letters
            WHERE share_token = %s
              AND published = TRUE
            """,
            (share_token,),
        ).fetchone()

    finally:
        connection.close()


def get_public_letters(limit=50, offset=0):
    """Return published letters for public discovery."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                title,
                body,
                created_at,
                updated_at
            FROM letters
            WHERE published = TRUE
            AND sealed = FALSE
            ORDER BY updated_at DESC, id DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

    finally:
        connection.close()


def get_public_letter_by_id(letter_id):
    """Return a letter only if it is published and not sealed."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                title,
                body,
                created_at,
                updated_at
            FROM letters
            WHERE id = %s
              AND published = TRUE
              AND sealed = FALSE
            """,
            (letter_id,),
        ).fetchone()

    finally:
        connection.close()


def unpublish_letter(owner_id, letter_id):
    """Revoke a share link only when the letter belongs to the owner."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            UPDATE letters
            SET published = FALSE,
                share_token = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND published = TRUE
            RETURNING id, owner_id, title, sealed, published, share_token
            """,
            (letter_id, owner_id),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def restore_missing_letters_for_owner(owner_id, letters):
    """Restore missing letters into one owner's collection only."""
    if not owner_id:
        raise ValueError("An owner ID is required.")

    connection = get_connection()
    imported = 0
    skipped = 0

    try:
        for letter in letters:
            created_at = datetime.strptime(
                letter["created_at"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)

            updated_at = datetime.strptime(
                letter["updated_at"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)

            existing = connection.execute(
                """
                SELECT id
                FROM letters
                WHERE owner_id = %s
                  AND title = %s
                  AND recipient = %s
                  AND body = %s
                  AND date_trunc('second', created_at)
                      = date_trunc('second', %s::timestamptz)
                  AND date_trunc('second', updated_at)
                      = date_trunc('second', %s::timestamptz)
                  AND sealed = %s
                LIMIT 1
                """,
                (
                    owner_id,
                    letter["title"],
                    letter["recipient"],
                    letter["body"],
                    created_at,
                    updated_at,
                    letter["sealed"],
                ),
            ).fetchone()

            if existing is not None:
                skipped += 1
                continue

            connection.execute(
                """
                INSERT INTO letters (
                    owner_id, title, recipient, body,
                    created_at, updated_at, sealed
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    owner_id,
                    letter["title"],
                    letter["recipient"],
                    letter["body"],
                    created_at,
                    updated_at,
                    letter["sealed"],
                ),
            )

            imported += 1

        connection.commit()
        return {"imported": imported, "skipped": skipped}

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def create_user(username, email, password_hash):
    """Create a user account using an already-hashed password."""
    if not username or not email or not password_hash:
        raise ValueError("Username, email, and password hash are required.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email, created_at
            """,
            (username, email, password_hash),
        ).fetchone()

        connection.commit()
        return row

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_user_by_username_or_email(identifier):
    """Find a user by username or email for account verification."""
    if not identifier:
        return None

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, username, email, password_hash, created_at
            FROM users
            WHERE LOWER(username) = LOWER(%s)
               OR LOWER(email) = LOWER(%s)
            LIMIT 1
            """,
            (identifier, identifier),
        ).fetchone()

    finally:
        connection.close()