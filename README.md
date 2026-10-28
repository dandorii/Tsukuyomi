# Tsukuyomi: Letters for the Unknown

*A quiet digital space for reflection, personal writing, and letters that don't always need to be sent.*

**Current Version:** 1.1.0  
**Initial Release:** 1.0.0  
**Repository:** [dandorii/Tsukuyomi](https://github.com/dandorii/Tsukuyomi)

## About

**Tsukuyomi: Letters for the Unknown** is a reflective writing archive built to provide a quiet, moonlit space for writing and preserving personal letters.

Inspired by midnight skies, pixel-art aesthetics, and the feeling of putting unspoken thoughts into words, Tsukuyomi focuses on a simple idea: some letters are valuable even when they are never sent.

The project combines a Flask application with PostgreSQL storage and a custom retro-inspired interface.

## Features

- **Reflective writing space** — Write letters in a calm, night-themed interface.
- **Draft management** — Save, browse, reopen, edit, and delete letters.
- **Persistent storage** — Store letters in a PostgreSQL database hosted by Neon.
- **Anonymous visitor sessions** — Associate each browser session's letter collection with a server-generated visitor ID.
- **Sealed letters** — Mark a letter as sealed and prevent normal editing or deletion through the application.
- **Shareable letters** — Publish a letter through a unique link and revoke its published status later.
- **Backup and restoration** — Export letters to a JSON backup and restore supported backups.
- **Responsive, retro-inspired design** — A midnight-blue visual style with moon and star motifs.

Feature availability and behavior should be verified against the deployed version before a public production release.

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

**Important:** This is anonymous, browser-session-based storage, not a user account system. The database persists letters, but access to a collection depends on retaining the associated session.

## Current Limitations

### Version 1.0.0 — Initial Release

Version 1.0.0 established the core writing and archive experience. Its limitations included:

1. **No user accounts:** There is no Tsukuyomi registration, login, or account-recovery system.
2. **Browser-session-dependent access:** Drafts are associated with an anonymous session. Different browsers and private browsing sessions normally have separate collections.
3. **No automatic cross-device synchronization:** A visitor cannot sign in on another device to retrieve the same collection.
4. **Session loss can mean loss of access:** Clearing browser cookies, losing the session, or using a different browser may make existing drafts inaccessible through the application. A database record may still exist even when the visitor no longer has the session needed to retrieve it.
5. **Backup responsibility:** Visitors should export and securely retain their own backups. Restoration should be tested with care.
6. **Share links are not private to their holder:** Anyone who obtains a published letter's unique link may be able to read that letter. Revoking the link prevents access through the application's published-link lookup, but cannot remove copies, screenshots, or content already obtained by others.
7. **No in-platform replies:** Shared letters are intended for reading, not ongoing conversations within Tsukuyomi.
8. **No guarantee of permanent storage or availability:** Service interruptions, hosting changes, database failures, or configuration issues may affect access. Keep independent backups of important writing.
9. **Security testing is ongoing:** Ownership checks and session protections require testing, and the application has not been independently security-audited.
10. **Preview deployment restrictions:** During development, Vercel Preview may be protected by Deployment Protection. Preview access is not the same as public production availability.

### Version 1.1.0 — Improvements and Remaining Limitations

Version 1.1.0 continues development of the existing writing and archive experience. The following items remain limitations or require verification based on the current implementation:

1. **Visitor ownership consistency:** Some existing published letters have owner IDs that do not match the current visitor session. The cause needs to be confirmed, and access to affected letters must be handled without weakening ownership checks.
2. **Owner-only unpublishing:** The unpublish operation must verify that the current visitor owns the letter. The button's visibility and the server-side authorization both require testing.
3. **Session persistence:** The Flask secret key must remain stable across restarts and deployments. A changed or missing key can invalidate existing session cookies and make previously saved letters inaccessible through the current session.
4. **No account-based ownership:** Visitor-based ownership remains different from authenticated account ownership. Signing in does not automatically mean existing visitor-owned letters have been migrated to an account.
5. **No cross-device recovery:** Without an account-based recovery mechanism, visitors still depend on their existing session or their own backups to access their letter collections.
6. **Publication privacy:** Publicly shared letters remain accessible to anyone who obtains a valid share link. Unpublishing cannot undo copies or screenshots already made.
7. **Security verification:** Changes to publishing, unpublishing, session handling, and ownership need regression tests before being considered production-ready.
8. **Deployment configuration:** Local, Preview, and Production environments must use the correct database settings and stable, environment-appropriate secrets.

These limitations should be revised as fixes are implemented and verified. A planned improvement must not be presented as a completed feature.

## Privacy and Security Notes

- The application uses server-generated anonymous visitor IDs to associate drafts with sessions.
- Database queries use parameterized values and owner-based filters for private letter operations.
- Flask session cookies are intended to use `HttpOnly` and `SameSite=Lax`; the `Secure` setting should be verified against the actual deployment configuration.
- Database credentials and the Flask secret key must be provided through environment variables and must not be committed to the repository.
- Do not store sensitive or highly confidential information in this version unless you understand and accept its limitations.

These measures are implementation details, not a substitute for a complete security review, deployment hardening, and testing.

## Local Development

### Requirements

- Python 3.13 or another version supported by the project's dependencies
- A PostgreSQL database, such as a Neon development database
- Git

### Setup

**1. Clone the repository.**

```bash
git clone https://github.com/dandorii/Tsukuyomi.git
cd Tsukuyomi
```

**2. Create and activate a virtual environment.**

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies.**

```powershell
python -m pip install -r requirements.txt
```

**4. Configure environment variables.**

Create a local `.env` file in the project root and configure the variables required by the application.

```dotenv
FLASK_SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=replace-with-your-postgresql-connection-string
```

Confirm the exact database variable name and `.env` loading behavior in the current code. Never commit `.env` or expose real credentials in public issues or documentation.

**5. Start the application.**

```powershell
python app.py
```

**6. Open the local URL** shown by Flask in your browser.

The database connection must point to a PostgreSQL database you control. The application initializes the required table and index when it starts, according to its current implementation.

## Environment Variables

| Variable | Purpose |
|---|---|
| `FLASK_SECRET_KEY` | Signs Flask session cookies. Use a strong, random secret and keep it stable for the relevant environment. |
| `DATABASE_URL` | PostgreSQL connection string for the selected environment, if this is the variable expected by the current database code. |
| `VERCEL` | Set by Vercel; used by the application for deployment-specific behavior. |
| `FLASK_ENV` | Include only if the current application code actually uses it to determine environment behavior. |

Configure environment variables separately for local development and deployment. Ensure Vercel Preview and Production point to the intended databases and use appropriate secrets.

## Roadmap

Possible future improvements include:

- User registration and authentication
- Secure access to letters across devices
- Account recovery and optional two-factor authentication
- Expanded privacy and retention controls
- Additional automated tests and security reviews
- Further accessibility and usability improvements
- More reliable ownership recovery for session-based letters

These items are planned possibilities, not promises or features currently available in version 1.1.0.

## Versioning

Tsukuyomi follows semantic versioning:

- **Patch** (`1.1.x`) — Bug fixes and small corrections
- **Minor** (`1.x.0`) — Backward-compatible features and improvements
- **Major** (`x.0.0`) — Substantial changes that may affect existing behavior

## Release History

### Version 1.0.0 — Initial Release

Established the core Tsukuyomi writing archive, including the writing interface, draft management, PostgreSQL persistence, anonymous visitor sessions, sealed letters, shareable letters, and backup functionality, subject to the behavior of the deployed implementation.

### Version 1.1.0 — Current Development Version

Continues development of the existing application, with attention to publication management, ownership consistency, session persistence, privacy, and reliability.

Add specific new features and fixes here as they are completed and verified.

## Project Philosophy

Tsukuyomi is built around reflection, gentleness, and the freedom to write without the expectation of a response.

Not every letter has to be sent. Not every thought needs an audience. Sometimes, writing something down is enough.

---

*Tsukuyomi: Letters for the Unknown — a quiet place beneath the same moon.*
