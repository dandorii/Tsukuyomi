import json
import os
import secrets
from flask import Flask, render_template, request, jsonify, session, url_for
from postgres_database import (
    initialize_database as initialize_postgres_database,
    save_letter,
    get_letters_by_owner,
    get_letter_by_owner,
    update_letter,
    delete_letter,
    seal_letter as seal_postgres_letter,
    publish_letter,
    get_published_letter,
    unpublish_letter,
    restore_missing_letters_for_owner,
)
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

secret_key = os.environ.get("FLASK_SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. Configure it in .env "
        "for local development or your deployment environment."
    )

app.config["SECRET_KEY"] = secret_key
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# Protect the session cookie.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("VERCEL") == "1"
    or os.environ.get("FLASK_ENV") == "production"
)

def get_visitor_id():
    """Return the current visitor's server-generated anonymous ID."""
    if "visitor_id" not in session:
        session["visitor_id"] = secrets.token_urlsafe(32)

    return session["visitor_id"]

initialize_postgres_database()

def validate_backup(data):
    """Validate a Tsukuyomi JSON backup before restoring letters."""
    if not isinstance(data, dict):
        return None, "The backup must contain a JSON object."

    if data.get("app") != "Tsukuyomi: Letters for the Unknown":
        return None, "This file is not a Tsukuyomi backup."

    if data.get("backup_version") != 2 or isinstance(
    data.get("backup_version"), bool
    ):
        return None, (
            "Only version-2 Tsukuyomi backups are supported. "
            "Legacy version-1 backups remain separate."
        )

    letters = data.get("letters")

    if not isinstance(letters, list):
        return None, "The backup must contain a list of letters."

    if len(letters) > 5000:
        return None, "The backup contains too many letters."

    validated_letters = []

    for index, letter in enumerate(letters, start=1):
        if not isinstance(letter, dict):
            return None, f"Letter {index} must be a JSON object."

        title = letter.get("title")
        recipient = letter.get("recipient")
        body = letter.get("body")
        created_at = letter.get("created_at")
        updated_at = letter.get("updated_at")
        sealed = letter.get("sealed")

        if not all(
            isinstance(value, str)
            for value in (
                title, recipient, body, created_at, updated_at
            )
        ):
            return None, f"Letter {index} has invalid text fields."

        if (
            len(title) > 100
            or len(recipient) > 100
            or len(body) > 100_000
        ):
            return None, f"Letter {index} exceeds the field limits."

        if not any(value.strip() for value in (title, recipient, body)):
            return None, f"Letter {index} is empty."

        if type(sealed) is not bool:
            return None, f"Letter {index} has an invalid sealed status."

        for timestamp in (created_at, updated_at):
            try:
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None, f"Letter {index} has an invalid timestamp."

        validated_letters.append({
            "title": title,
            "recipient": recipient,
            "body": body,
            "created_at": created_at,
            "updated_at": updated_at,
            "sealed": sealed,
        })

    return validated_letters, None

def format_letter_timestamp(timestamp):
    if not timestamp:
        return "Unknown date"

    try:
        date = datetime.strptime(
            timestamp, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        manila_time = date.astimezone(
            timezone(timedelta(hours=8))
        )

        return manila_time.strftime("%b %d, %Y · %H:%M")

    except (TypeError, ValueError):
        return timestamp


def serialize_timestamp(value):
    """Convert database timestamps into JSON-safe strings."""
    if isinstance(value, datetime):
        return value.isoformat()

    return value


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/archive")
def archive():
    return render_template("archive.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/shared/<string:share_token>")
def shared_letter(share_token):
    shared_letter = get_published_letter(share_token)

    if shared_letter is None:
        return render_template("letter-not-found.html"), 404

    shared_letter = dict(shared_letter)

    shared_letter["created_at_display"] = format_letter_timestamp(
        shared_letter["created_at"].astimezone(
            timezone(timedelta(hours=8))
        ).strftime("%Y-%m-%d %H:%M:%S")
    )

    return render_template(
        "shared-letter.html",
        shared_letter=shared_letter,
    )


@app.route("/api/drafts/<int:draft_id>/publish", methods=["POST"])
def publish_draft(draft_id):
    published = publish_letter(get_visitor_id(), draft_id)

    if published is None:
        return jsonify({
            "error": "Letter not found or already published."
        }), 404

    share_url = url_for(
        "shared_letter",
        share_token=published["share_token"],
        _external=True,
    )

    return jsonify({
        "message": "Letter published. Anyone with the link can read it.",
        "id": published["id"],
        "published": True,
        "share_url": share_url,
    }), 200


@app.route("/api/drafts/<int:draft_id>/unpublish", methods=["POST"])
def unpublish_draft(draft_id):
    result = unpublish_letter(get_visitor_id(), draft_id)

    if result is None:
        return jsonify({
            "error": "Letter not found or not published."
        }), 404

    return jsonify({
        "message": "Share link revoked. The letter is private again.",
        "id": result["id"],
        "published": False,
    }), 200


@app.route("/reflection")
def reflection():
    return render_template("reflection.html")


@app.route("/reflection/leave-behind")
def reflection_leave_behind():
    return render_template("reflection-leave-behind.html")


@app.route("/write")
def writing_room():
    return render_template("writing-room.html")


@app.route("/my-letters")
def my_letters():
    return render_template("my-letters.html")


@app.route("/my-letters/<int:draft_id>")
def read_letter(draft_id):
    from postgres_database import get_letter_by_owner

    draft = get_letter_by_owner(get_visitor_id(), draft_id)

    if draft is None:
        return render_template("letter-not-found.html"), 404

    draft["created_at_display"] = format_letter_timestamp(
        draft["created_at"].astimezone(
            timezone(timedelta(hours=8))
        ).strftime("%Y-%m-%d %H:%M:%S")
    )
    draft["updated_at_display"] = format_letter_timestamp(
        draft["updated_at"].astimezone(
            timezone(timedelta(hours=8))
        ).strftime("%Y-%m-%d %H:%M:%S")
    )

    draft["published"] = bool(draft.get("published"))

    draft["share_url"] = ""

    if draft["published"] and draft.get("share_token"):
        draft["share_url"] = url_for(
            "shared_letter",
            share_token=draft["share_token"],
            _external=True,
        )

    return render_template("read-letter.html", draft=draft)


@app.route("/api/drafts", methods=["POST"])
def create_draft():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    title = data.get("title", "")
    recipient = data.get("recipient", "")
    body = data.get("body", "")

    if not all(isinstance(value, str) for value in (title, recipient, body)):
        return jsonify({"error": "All fields must be text."}), 400

    if not any(value.strip() for value in (title, recipient, body)):
        return jsonify({"error": "Write something before saving."}), 400

    if len(title) > 100 or len(recipient) > 100 or len(body) > 100_000:
        return jsonify({"error": "One or more fields are too long."}), 400

    draft = save_letter(
        get_visitor_id(),
        title.strip(),
        recipient.strip(),
        body,
    )

    return jsonify({
        "message": "Draft saved successfully.",
        "id": draft["id"],
    }), 201


@app.route("/api/drafts", methods=["GET"])
def list_drafts():
    drafts = get_letters_by_owner(get_visitor_id())

    return jsonify({
        "drafts": [
            {
                "id": draft["id"],
                "title": draft["title"],
                "recipient": draft["recipient"],
                "created_at": serialize_timestamp(draft["created_at"]),
                "updated_at": serialize_timestamp(draft["updated_at"]),
                "sealed": bool(draft["sealed"]),
            }
            for draft in drafts
        ]
    }), 200


@app.route("/api/drafts/export", methods=["GET"])
def export_drafts():
    drafts = get_letters_by_owner(get_visitor_id())
    letters = []

    for draft in drafts:
        letters.append({
            "id": draft["id"],
            "title": draft["title"],
            "recipient": draft["recipient"],
            "body": draft["body"],
            "created_at": draft["created_at"].astimezone(
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": draft["updated_at"].astimezone(
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "sealed": bool(draft["sealed"]),
        })

    backup = {
        "app": "Tsukuyomi: Letters for the Unknown",
        "backup_version": 2,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "letters": letters,
    }

    response = jsonify(backup)
    response.headers["Content-Disposition"] = (
        'attachment; filename="tsukuyomi-backup.json"'
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response, 200


@app.route("/api/drafts/restore", methods=["POST"])
def restore_drafts():
    backup_file = request.files.get("backup")

    if backup_file is None or not backup_file.filename:
        return jsonify({
            "error": "Choose a JSON backup file first."
        }), 400

    if not backup_file.filename.lower().endswith(".json"):
        return jsonify({
            "error": "Only JSON backup files are accepted."
        }), 400

    try:
        data = json.load(backup_file.stream)
    except (ValueError, UnicodeDecodeError):
        return jsonify({
            "error": "The file is not valid JSON."
        }), 400

    validated_letters, error = validate_backup(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        result = restore_missing_letters_for_owner(
            get_visitor_id(),
            validated_letters,
        )
    except Exception:
        app.logger.exception("Backup restoration failed.")
        return jsonify({
            "error": "The backup could not be restored. No changes were saved."
        }), 500

    return jsonify({
        "message": "Backup restoration completed.",
        "imported": result["imported"],
        "skipped": result["skipped"],
    }), 200


@app.route("/api/drafts/<int:draft_id>", methods=["GET"])
def retrieve_draft(draft_id):
    draft = get_letter_by_owner(get_visitor_id(), draft_id)

    if draft is None:
        return jsonify({"error": "Letter not found."}), 404

    return jsonify({
        "draft": {
            "id": draft["id"],
            "title": draft["title"],
            "recipient": draft["recipient"],
            "body": draft["body"],
            "created_at": serialize_timestamp(draft["created_at"]),
            "updated_at": serialize_timestamp(draft["updated_at"]),
            "sealed": bool(draft["sealed"]),
        }
    }), 200


@app.route("/api/drafts/<int:draft_id>", methods=["PUT"])
def edit_draft(draft_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    title = data.get("title", "")
    recipient = data.get("recipient", "")
    body = data.get("body", "")

    if not all(
        isinstance(value, str)
        for value in (title, recipient, body)
    ):
        return jsonify({"error": "All fields must be text."}), 400

    if not any(value.strip() for value in (title, recipient, body)):
        return jsonify({"error": "Write something before saving."}), 400

    if len(title) > 100 or len(recipient) > 100 or len(body) > 100_000:
        return jsonify({"error": "One or more fields are too long."}), 400

    updated = update_letter(
        get_visitor_id(),
        draft_id,
        title.strip(),
        recipient.strip(),
        body,
    )

    if updated is None:
        return jsonify({
            "error": "Letter not found, or it is sealed."
        }), 404

    return jsonify({
        "message": "Draft updated successfully.",
        "id": updated["id"],
    }), 200


@app.route("/api/drafts/<int:draft_id>", methods=["DELETE"])
def remove_draft(draft_id):
    deleted = delete_letter(get_visitor_id(), draft_id)

    if not deleted:
        return jsonify({"error": "Letter not found or cannot be deleted."}), 404

    return jsonify({
        "message": "Draft deleted successfully.",
        "id": draft_id,
    }), 200


@app.route("/api/drafts/<int:draft_id>/seal", methods=["POST"])
def seal_draft_route(draft_id):
    sealed = seal_postgres_letter(get_visitor_id(), draft_id)

    if sealed is None:
        return jsonify({
            "error": "Letter not found or already sealed."
        }), 404

    return jsonify({
        "message": "Letter sealed permanently. It has not been sent.",
        "id": sealed["id"],
        "sealed": True,
    }), 200


if __name__ == "__main__":
    app.run(debug=True)