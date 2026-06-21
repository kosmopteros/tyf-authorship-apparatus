# Project contracts

_Static-confidence operational surface — how this repo is built, run, and configured. Environment variables are listed by NAME only and real `.env` files are never opened (only `.env*.example` templates); script and Dockerfile command strings are shown with likely inline secrets redacted, but treat them as untrusted and review before sharing._

## Scripts (package.json)

- `install-skills`: `bash scripts/install.sh`

## Config / DB surface

- `pyproject.toml`

## Environment contract (names only)

- referenced in code (4): `TYF_LATEST_TAG`, `TYF_NO_DOC_HOOK`, `TYF_PACK_ROOT`, `TYF_UPDATE_CACHE`
- **used in code but not in any `.env*.example`** (4): `TYF_LATEST_TAG`, `TYF_NO_DOC_HOOK`, `TYF_PACK_ROOT`, `TYF_UPDATE_CACHE`
