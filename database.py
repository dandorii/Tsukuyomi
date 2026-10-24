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
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
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
    """Return all drafts, newest updated first."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, title, recipient, created_at, updated_at
            FROM letters
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

def update_draft(draft_id, title, recipient, body):
    """Update an existing draft and report whether it exists."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE letters
            SET title = ?,
                recipient = ?,
                body = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, recipient, body, draft_id),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()

def delete_draft(draft_id):
    """Delete a draft by its ID and report whether it existed."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM letters WHERE id = ?",
            (draft_id,),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()
