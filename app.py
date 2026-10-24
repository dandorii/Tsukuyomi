import json
from flask import Flask, render_template, request, jsonify
from database import (
    initialize_database,
    save_draft,
    get_all_drafts,
    get_draft,
    update_draft,
    delete_draft,
    seal_draft,
    restore_missing_letters,
)
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

initialize_database()

def validate_backup(data):
    """Validate a Tsukuyomi JSON backup before restoring letters."""
    if not isinstance(data, dict):
        return None, "The backup must contain a JSON object."

    if data.get("app") != "Tsukuyomi: Letters for the Unknown":
        return None, "This file is not a Tsukuyomi backup."

    if data.get("backup_version") != 1 or isinstance(
        data.get("backup_version"), bool
    ):
        return None, "This backup version is not supported."

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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/archive")
def archive():
    return render_template("archive.html")


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
    draft = get_draft(draft_id)

    if draft is None:
        return render_template("letter-not-found.html"), 404

    draft = dict(draft)

    draft["created_at_display"] = format_letter_timestamp(
        draft["created_at"]
    )
    draft["updated_at_display"] = format_letter_timestamp(
        draft["updated_at"]
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

    draft_id = save_draft(title.strip(), recipient.strip(), body)

    return jsonify({
        "message": "Draft saved successfully.",
        "id": draft_id
    }), 201


@app.route("/api/drafts", methods=["GET"])
def list_drafts():
    drafts = get_all_drafts()

    return jsonify({
        "drafts": [
            {
                "id": draft["id"],
                "title": draft["title"],
                "recipient": draft["recipient"],
                "created_at": draft["created_at"],
                "updated_at": draft["updated_at"],
                "sealed": bool(draft["sealed"]),
            }
            for draft in drafts
        ]
    }), 200


@app.route("/api/drafts/export", methods=["GET"])
def export_drafts():
    drafts = get_all_drafts()
    letters = []

    for draft in drafts:
        full_letter = get_draft(draft["id"])

        if full_letter is None:
            return jsonify({
                "error": "A letter could not be retrieved. No backup was created."
            }), 500

        letters.append({
            "id": full_letter["id"],
            "title": full_letter["title"],
            "recipient": full_letter["recipient"],
            "body": full_letter["body"],
            "created_at": full_letter["created_at"],
            "updated_at": full_letter["updated_at"],
            "sealed": bool(full_letter["sealed"]),
        })

    backup = {
        "app": "Tsukuyomi: Letters for the Unknown",
        "backup_version": 1,
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
        result = restore_missing_letters(validated_letters)
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
    draft = get_draft(draft_id)

    if draft is None:
        return jsonify({"error": "Letter not found."}), 404

    return jsonify({
        "draft": {
            "id": draft["id"],
            "title": draft["title"],
            "recipient": draft["recipient"],
            "body": draft["body"],
            "created_at": draft["created_at"],
            "updated_at": draft["updated_at"],
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

    existing_draft = get_draft(draft_id)

    if existing_draft is None:
        return jsonify({"error": "Letter not found."}), 404

    updated = update_draft(
        draft_id,
        title.strip(),
        recipient.strip(),
        body
    )

    if not updated:
        return jsonify({
            "error": "This letter is sealed or no longer exists."
        }), 409

    return jsonify({
        "message": "Draft updated successfully.",
        "id": draft_id
    }), 200


@app.route("/api/drafts/<int:draft_id>", methods=["DELETE"])
def remove_draft(draft_id):
    deleted = delete_draft(draft_id)

    if not deleted:
        return jsonify({"error": "Letter not found."}), 404

    return jsonify({
        "message": "Draft deleted successfully.",
        "id": draft_id
    }), 200


@app.route("/api/drafts/<int:draft_id>/seal", methods=["POST"])
def seal_letter(draft_id):
    draft = get_draft(draft_id)

    if draft is None:
        return jsonify({"error": "Letter not found."}), 404

    if draft["sealed"]:
        return jsonify({"error": "This letter is already sealed."}), 409

    sealed = seal_draft(draft_id)

    if not sealed:
        return jsonify({
            "error": "This letter could not be sealed."
        }), 409

    return jsonify({
        "message": "Letter sealed permanently. It has not been sent.",
        "id": draft_id,
        "sealed": True
    }), 200


if __name__ == "__main__":
    app.run(debug=True)