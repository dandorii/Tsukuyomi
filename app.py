from flask import Flask, render_template, request, jsonify
from database import initialize_database, save_draft, get_all_drafts, get_draft, update_draft, delete_draft


app = Flask(__name__)


initialize_database()


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
            }
            for draft in drafts
        ]
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

    update_draft(
        draft_id,
        title.strip(),
        recipient.strip(),
        body
    )

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


if __name__ == "__main__":
    app.run(debug=True)