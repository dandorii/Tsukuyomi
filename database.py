import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "tsukuyomi.db"


def get_connection():
    """Create a connection to the Tsukuyomi database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    """Create the letters table if it does not exist."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '',
                recipient TEXT NOT NULL DEFAULT '',
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sealed INTEGER NOT NULL DEFAULT 0
                    CHECK (sealed IN (0, 1))
            )
            """
        )

        # Add the column to existing databases if it is missing.
        columns = connection.execute(
            "PRAGMA table_info(letters)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "sealed" not in column_names:
            connection.execute(
                """
                ALTER TABLE letters
                ADD COLUMN sealed INTEGER NOT NULL DEFAULT 0
                    CHECK (sealed IN (0, 1))
                """
            )

        connection.commit()
    finally:
        connection.close()

def save_draft(title, recipient, body):
    """Save a new letter draft and return its database ID."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO letters (title, recipient, body)
            VALUES (?, ?, ?)
            """,
            (title, recipient, body),
        )

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def restore_missing_letters(letters):
    """Restore missing letters without overwriting existing records."""
    connection = get_connection()

    imported = 0
    skipped = 0

    try:
        # Reserve the write transaction before checking for duplicates.
        connection.execute("BEGIN IMMEDIATE")

        existing_letters = connection.execute(
            """
            SELECT title, recipient, body, created_at, updated_at, sealed
            FROM letters
            """
        ).fetchall()

        def duplicate_key(letter):
            return (
                letter["title"],
                letter["recipient"],
                letter["body"],
                letter["created_at"],
                letter["updated_at"],
                int(letter["sealed"]),
            )

        known_keys = {
            duplicate_key(letter)
            for letter in existing_letters
        }

        for letter in letters:
            key = duplicate_key(letter)

            if key in known_keys:
                skipped += 1
                continue

            connection.execute(
                """
                INSERT INTO letters (
                    title,
                    recipient,
                    body,
                    created_at,
                    updated_at,
                    sealed
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    letter["title"],
                    letter["recipient"],
                    letter["body"],
                    letter["created_at"],
                    letter["updated_at"],
                    int(letter["sealed"]),
                ),
            )

            known_keys.add(key)
            imported += 1

        connection.commit()

        return {
            "imported": imported,
            "skipped": skipped,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_draft(draft_id):
    """Retrieve one draft by its ID."""
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT * FROM letters WHERE id = ?",
            (draft_id,),
        ).fetchone()
    finally:
        connection.close()


def get_all_drafts():
    """Return all letters, newest updated first."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, title, recipient, created_at, updated_at, sealed
            FROM letters
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()


def update_draft(draft_id, title, recipient, body):
    """Update an unsealed draft and report whether it was updated."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE letters
            SET title = ?,
                recipient = ?,
                body = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND sealed = 0
            """,
            (title, recipient, body, draft_id),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()

        
def seal_draft(draft_id):
    """Permanently seal an existing, unsealed letter."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE letters
            SET sealed = 1
            WHERE id = ? AND sealed = 0
            """,
            (draft_id,),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_draft(draft_id):
    """Delete an unsealed draft and report whether it was deleted."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM letters
            WHERE id = ? AND sealed = 0
            """,
            (draft_id,),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()