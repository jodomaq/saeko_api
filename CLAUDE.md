# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**saekoAuth** is a Python toolkit for integrating with the Saeko API (educational institution management platform used by CECYTEM). It provides OAuth2 authentication, GUI applications for data export, and utilities for institutional data management.

## Setup & Running

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy .env and fill in service account credentials
# (see .env for required variables)
```

**Run each script directly — no build step:**
```bash
python auth.py                          # Test authentication, print tokens
python api.py                           # Test API wrapper functions
python saeko_csv_app.py                 # Launch CSV export GUI
python saeko_enrollment_summary_app.py  # Launch enrollment matrix GUI
python descargar_planes.py              # Download study plans from COSAC SEMS
```

No test framework or linting configuration exists.

## Architecture

### Authentication Flow (`auth.py`)
- Loads RSA private key and service account config from `.env`
- Builds a JWT signed with RS256 (`build_jwt()`)
- Exchanges JWT for an OAuth2 Bearer access token via `POST /oauth/token` (`get_access_token()`)
- All other modules call `get_access_token()` at startup to obtain a Bearer token

### Module Responsibilities
| File | Purpose |
|------|---------|
| `auth.py` | OAuth2 JWT-Bearer auth; token refresh; token persistence |
| `api.py` | Thin wrappers over core Saeko endpoints (terms, schools) |
| `saeko_csv_app.py` | Tkinter GUI: cascading school→term→program→group filters, paginated enrollment export to CSV |
| `saeko_enrollment_summary_app.py` | Tkinter GUI: enrollment count matrix (schools × terms) exported to Excel |
| `descargar_planes.py` | Web scraper for study plans from COSAC SEMS; downloads PDFs/ZIPs into `planes_de_estudio/` |

### Key Patterns
- **GUI threading**: Both Tkinter apps use `threading.Thread(daemon=True)` for all API calls to keep the UI responsive.
- **Pagination**: Enrollment queries use `limit=500` and loop until `meta.next_page` is null.
- **Cascading dropdowns**: Selecting a school triggers loading terms + programs; selecting a term triggers loading groups.
- **Environment config**: All credentials and URLs come from `.env` via `python-dotenv`. Never hardcode them.

### API Base URL
`https://app.saeko.io/api/v1` — full endpoint reference in `api_doc.md` (833 endpoints across 32 modules).

### Required `.env` Variables
```
SAEKO_AUTH_URL=https://app.saeko.io/oauth/token
SAEKO_API_URL=https://app.saeko.io
SAEKO_CLIENT_ID=...
SAEKO_PRIVATE_KEY_ID=...
SAEKO_PRIVATE_KEY=...   # RSA 2048-bit private key (PEM format)
SAEKO_EXPIRES_AT=...
SAEKO_USER_EMAIL=...
```
