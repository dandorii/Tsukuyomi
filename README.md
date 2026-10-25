# Tsukuyomi: Letters for the Unknown 🌙

*A quiet digital space for reflection, personal writing, and letters that don't always need to be sent.*

**Version:** 1.0.0   
**Repository:** [dandorii/Tsukuyomi](https://github.com/dandorii/Tsukuyomi)

## About

**Tsukuyomi: Letters for the Unknown** is a reflective writing archive built to provide a quiet, moonlit space for writing and preserving personal letters.

Inspired by midnight skies, pixel-art aesthetics, and the feeling of putting unspoken thoughts into words, Tsukuyomi focuses on a simple idea: some letters are valuable even when they are never sent.

The project combines a Flask application with PostgreSQL storage and a custom retro-inspired interface.

## Features

- **Reflective writing space** — write letters in a calm, night-themed interface.
- **Draft management** — save, browse, reopen, edit, and delete letters.
- **Persistent storage** — store letters in a PostgreSQL database hosted by Neon.
- **Anonymous visitor sessions** — keep each browser session's letter collection associated with its own server-generated visitor ID.
- **Sealed letters** — mark a letter as sealed and prevent normal editing or deletion through the application.
- **Shareable letters** — publish a letter through a unique link and revoke its published status later.
- **Backup and restoration** — export letters to a JSON backup and restore supported backups.
- **Responsive, retro-inspired design** — a midnight-blue visual style with moon and star motifs.

> Feature availability and behavior should be verified against the deployed version before a public production release.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Database hosting | Neon |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Vercel |
| Database driver | Psycopg |

## How Draft Storage Works

Tsukuyomi stores letters in PostgreSQL. Each anonymous visitor receives a server-generated visitor ID held in a Flask session. Draft retrieval and modification operations use that ID to restrict access to the corresponding visitor's letters.

**Important:** This is anonymous, browser-session-based storage—not a user account system. The database persists letters, but access to a collection depends on retaining the associated session.

## Current Limitations

Version 1.0.0 intentionally keeps the project focused. The following limitations are part of the current design:

1. **No user accounts:** There is no Tsukuyomi registration, login, or account-recovery system.
2. **Browser-session-dependent access:** Drafts are associated with an anonymous session. Different browsers and private browsing sessions normally have separate collections.
3. **No automatic cross-device synchronization:** A visitor cannot sign in on another device to retrieve the same collection.
4. **Session loss can mean loss of access:** Clearing browser cookies, losing the session, or using a different browser may make existing drafts inaccessible through the application. A database record may still exist even when the visitor no longer has the session needed to retrieve it.
5. **Backup responsibility:** Visitors should export and securely retain their own backups. Restoration should be tested with care.
6. **Share links are not private to their holder:** Anyone who obtains a published letter's unique link may be able to read that letter. Revoking the link prevents access through the application's published-link lookup, but cannot remove copies, screenshots, or content already obtained by others.
7. **No in-platform replies:** Shared letters are intended for reading, not ongoing conversations within Tsukuyomi.
8. **No guarantee of permanent storage or availability:** Service interruptions, hosting changes, database failures, or account and configuration issues may affect access. Keep independent backups of important writing.
9. **Security testing is ongoing:** Ownership checks and session protections are implemented, but the application should not be considered independently security-audited or guaranteed secure.
10. **Preview deployment:** During development and verification, Vercel Preview may be protected by Vercel Deployment Protection. Preview access is not the same as public production availability.

## Privacy and Security Notes

- The application uses server-generated anonymous visitor IDs to associate drafts with sessions.
- Database queries use parameterized values and owner-based filters for private letter operations.
- Flask session cookies are configured with `HttpOnly` and `SameSite=Lax`; the `Secure` setting is enabled when the relevant production or Vercel environment conditions apply.
- Database credentials and the Flask secret key should be provided through environment variables and must not be committed to the repository.
- Do not store sensitive or highly confidential information in this version unless you understand and accept its limitations.

These measures are implementation details, not a substitute for a complete security review, deployment hardening, and testing.

## Local Development

### Requirements

- Python 3.13 or another version supported by the project's installed dependencies
- A PostgreSQL database, such as a Neon development database
- Git

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/dandorii/Tsukuyomi.git
   cd Tsukuyomi
   ```

2. Create and activate a virtual environment.

   **Windows PowerShell:**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create a local `.env` file in the project root. Configure the required variables:

   ```dotenv
   FLASK_SECRET_KEY=replace-with-a-long-random-secret
   DATABASE_URL=replace-with-your-postgresql-connection-string
   ```

   Use your own development credentials. Never commit `.env` or paste real credentials into public issues or documentation.

5. Start the application:

   ```powershell
   python app.py
   ```

6. Open the local URL shown by Flask in your browser.

The database connection must point to a PostgreSQL database you control. The application initializes the required table and index when it starts.

## Environment Variables

| Variable | Purpose |
|---|---|
| `FLASK_SECRET_KEY` | Signs Flask session cookies. Use a strong, random secret. |
| `DATABASE_URL` | PostgreSQL connection string for the selected environment. |
| `VERCEL` | Set by Vercel; used by the application for deployment-specific behavior. |
| `FLASK_ENV` | Used by the application to determine whether secure-cookie behavior should be enabled for the configured environment. |

Configure environment variables separately for local development and deployment. Ensure Vercel Preview and Production point to the intended database and use appropriate secrets.

## Roadmap

Possible future improvements include:

- User registration and authentication
- Secure access to letters across devices
- Account recovery and optional two-factor authentication
- Expanded privacy and retention controls
- Additional automated tests and security reviews
- Further accessibility and usability improvements

These items are planned possibilities, not promises or features currently available in version 1.0.0.

## Versioning

Tsukuyomi follows semantic versioning:

- **Patch** (`1.0.x`): bug fixes and small corrections
- **Minor** (`1.x.0`): backward-compatible features
- **Major** (`x.0.0`): substantial changes that may affect existing behavior

## Project Philosophy

Tsukuyomi is built around reflection, gentleness, and the freedom to write without the expectation of a response.

Not every letter has to be sent. Not every thought needs an audience. Sometimes, writing something down is enough.

---

*Tsukuyomi: Letters for the Unknown — a quiet place beneath the same moon.*