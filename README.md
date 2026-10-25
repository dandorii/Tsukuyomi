# Tsukuyomi — Letters for the Unknown

*A quiet place for the words we keep, the letters we never send, and the thoughts we don't always know how to express.*

---

## About

Not every letter needs to be sent. Not every thought needs an answer.

**Tsukuyomi** is a personal writing space built around that idea. It is a place to slow down, put thoughts into words, preserve meaningful moments, and write letters that may or may not ever reach their intended recipient.

Inspired by the quiet atmosphere of midnight, handwritten letters, and nostalgic digital experiences, Tsukuyomi brings reflective writing into a small corner of the web.

It isn't about finding the perfect words. It's about having somewhere to leave them.

## What You Can Do

- **Write** — Compose letters in a dedicated writing room.
- **Keep** — Save drafts and return to them whenever you're ready.
- **Seal** — Preserve letters you aren't ready to change.
- **Share** — Give a letter its own link when you're ready for someone else to read it.
- **Revoke** — Disable a published letter's link when you no longer want it to be accessible.
- **Reflect** — Explore a quiet archive designed for thoughtful reading and writing.
- **Restore** — Export and restore supported letter data.

## The Experience

Tsukuyomi takes inspiration from midnight skies, pixel art, and nostalgic interfaces. Its visual identity uses deep blues, moonlit accents, pixel-inspired typography, and a restrained atmosphere intended to let the writing take center stage.

The goal is simple: create a digital space that feels less like another productivity tool and more like opening a letter beneath a quiet night sky.

## Built With

- Python
- Flask
- PostgreSQL
- Psycopg 3
- HTML, CSS, and JavaScript
- Jinja2

## Running Locally

### Requirements

- Python 3.13 or a compatible version
- A PostgreSQL database
- Git

### Setup

Clone the repository:

```bash
git clone https://github.com/dandorii/Tsukuyomi.git
cd Tsukuyomi
```

Create and activate a virtual environment using Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```dotenv
FLASK_SECRET_KEY=your_secure_secret
DATABASE_URL=your_postgresql_connection_string
```

Replace the example values with your own configuration. Keep `.env` private and never commit production secrets.

Start the application:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Development Status

Tsukuyomi is an ongoing project. Its core writing experience, PostgreSQL integration, and shareable-letter functionality are implemented, while deployment preparation, security review, and further testing remain in progress.

Before a public release, the application needs additional verification of session handling, access controls, request protections, and the behavior of shared letters.

## A Note on Privacy

Personal writing can be sensitive. Tsukuyomi is being developed with privacy in mind, including owner-scoped database operations and revocable sharing links.

However, the application is still under development and has not been presented as fully security-audited. Avoid storing highly sensitive information until the deployment and security controls have been properly reviewed.

## License

No license has been specified yet. All rights remain with the respective copyright holder unless a license is added.

---

*Some words are never sent.*

*Some memories are never forgotten.*

*And some letters are written simply because they need somewhere to exist.*
