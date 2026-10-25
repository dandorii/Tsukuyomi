
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

import app

app.app.config["TESTING"] = True

owner = app.app.test_client()
visitor = app.app.test_client()

# 1. Owner creates a private letter.
response = owner.post("/api/drafts", json={
    "title": "Temporary Sharing Test",
    "recipient": "Test Reader",
    "body": "This letter checks public sharing and revocation.",
})

assert response.status_code == 201, response.get_json()
letter_id = response.get_json()["id"]
print("Owner creates a letter: passed")

try:
    # 2. A different visitor cannot read it before publication.
    response = visitor.get(f"/api/drafts/{letter_id}")
    assert response.status_code == 404, response.get_json()
    print("Private letter stays hidden from other visitors: passed")

    # 3. Owner publishes it and receives a link.
    response = owner.post(f"/api/drafts/{letter_id}/publish")
    assert response.status_code == 200, response.get_json()

    share_url = response.get_json()["share_url"]
    share_path = urlparse(share_url).path
    print("Owner publishes the letter: passed")

    # 4. Another visitor can read it using the share link.
    response = visitor.get(share_path)
    assert response.status_code == 200, response.status_code
    assert b"Temporary Sharing Test" in response.data
    assert b"This letter checks public sharing" in response.data
    print("Published letter is readable through its link: passed")

    # 5. A different visitor cannot revoke the owner's link.
    response = visitor.post(f"/api/drafts/{letter_id}/unpublish")
    assert response.status_code == 404, response.get_json()
    print("Other visitors cannot revoke the owner's link: passed")

    # 6. Owner revokes the link.
    response = owner.post(f"/api/drafts/{letter_id}/unpublish")
    assert response.status_code == 200, response.get_json()
    print("Owner revokes the share link: passed")

    # 7. The old link no longer works.
    response = visitor.get(share_path)
    assert response.status_code == 404, response.status_code
    print("Revoked link no longer opens: passed")

finally:
    # Remove the temporary letter using the owner's session.
    owner.delete(f"/api/drafts/{letter_id}")

print("\nPublic sharing tests completed.")
