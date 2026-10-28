from dotenv import load_dotenv

load_dotenv()

from postgres_database import (
    save_letter,
    publish_letter,
    get_public_letters,
    delete_letter,
)


def test_public_library_only_returns_published_letters():
    owner_id = "test_public_library_owner"

    # Create one private letter and one letter to publish.
    private_letter = save_letter(
        owner_id,
        "Private Test Letter",
        "Private Reader",
        "This letter must stay private.",
    )

    public_letter = save_letter(
        owner_id,
        "Public Test Letter",
        "Public Reader",
        "This letter should appear in the library.",
    )

    try:
        # Publish only the second letter.
        published = publish_letter(owner_id, public_letter["id"])
        assert published is not None

        # Retrieve letters from the public library.
        public_letters = get_public_letters()

        public_ids = {letter["id"] for letter in public_letters}

        assert public_letter["id"] in public_ids
        assert private_letter["id"] not in public_ids

    finally:
        # Clean up both test letters.
        delete_letter(owner_id, private_letter["id"])
        delete_letter(owner_id, public_letter["id"])


def test_public_library_route_loads(client=None):
    from app import app

    with app.test_client() as client:
        response = client.get("/library")

        assert response.status_code == 200
        assert b"Public Library" in response.data
        assert b"TSUKUYOMI" in response.data