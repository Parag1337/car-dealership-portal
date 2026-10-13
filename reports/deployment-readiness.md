# Deployment Readiness — Render (local verification only)

**Date (UTC):** 2026-10-13
**Scope:** make the project safe to deploy via root `render.yaml`. **No commit, push,
deploy, production-data change, or secret exposure was performed.** Existing
`screenshots/` and `reports/` evidence was preserved untouched (one temporary
verification review was posted live and then deleted to keep DB state consistent
with the screenshots).

## 1. Issues found (and disposition)

| # | Issue | Severity | Disposition |
|---|---|---|---|
| 1 | `CORS_ALLOW_ALL_ORIGINS = True` in production (`settings.py`) | High | **Fixed:** removed; env-parsed allow-list, local origins dev-only, `*` rejected |
| 2 | `render.yaml` set `CORS_ALLOWED_ORIGINS` but code ignored it | Medium | **Fixed** by #1 (now consumed; also feeds `CSRF_TRUSTED_ORIGINS`) |
| 3 | Predictable default `SECRET_KEY` usable in production | High | **Fixed:** `ImproperlyConfigured` when `DEBUG=False` without env key |
| 4 | `ALLOWED_HOSTS` defaulted to `*`, even in production | High | **Fixed:** required + explicit in prod, `*` rejected |
| 5 | `populate_data` review seeding crashed on repeat (`MultipleObjectsReturned` once any same dealer+customer review exists) — proven by new test | High | **Fixed:** seed reviews keyed on `(dealer, customer, review_text)` |
| 6 | `build.sh` hid seed failures (`populate_data \|\| echo …`) | Medium | **Fixed:** failure now fails the build |
| 7 | CI `validate` job ran `manage.py check` without installing deps (would fail with `ModuleNotFoundError`) | Medium | **Fixed:** setup-python + requirements install in that job |
| 8 | CI ran `makemigrations` (creates files) instead of `--check`; lint scanned `.venv` and `flask8… || true` hid failures; Python 3.10 vs prod 3.11 | Medium | **Fixed:** `--check --dry-run`, scoped lint without `\|\| true`, Python 3.11, job renamed `validate-deployment`, branch gate removed |
| 9 | `DEPLOYMENT_INSTRUCTIONS.md` described Windows paths/Heroku-first flow and implied success | Medium | **Rewritten** to the real Blueprint flow |
| 10 | `check --deploy` W004 (no HSTS) | Low/Advisory | **Accepted deliberately:** HSTS risks lockout if misconfigured; redirect + secure cookies are on |
| 11 | gunicorn `--workers 4` on free-plan RAM; health-check vs `SECURE_SSL_REDIRECT`; free-DB retention | Unknown (runtime-only) | **Flagged, not changed:** cannot be resolved without a real deploy; listed below |
| 12 | Homepage test-client rendering 500s from Django 4.2 + Python 3.14 `copy(Context)` incompatibility (test harness only; live serving proven by browser) | Low (env) | **Worked around:** view-level assertions without template render |

## 2. Files changed and reasons

- `server/djangoproj/settings.py` — env-enforced `SECRET_KEY`/`ALLOWED_HOSTS` in prod; `_parse_origin_list`; dev-only local CORS; `CSRF_TRUSTED_ORIGINS` from explicit https origins. Same-origin production needs no CORS (Django serves the React build); no wildcards, no global CSRF weakening.
- `server/djangoapp/tests.py` — +6 tests: CORS parser/reflection/`ALLOW_ALL`-absent; homepage React-vs-fallback routing; `populate_data` triple-run idempotency incl. custom-password + user-review preservation. Suite: **27/27**.
- `server/djangoapp/management/commands/populate_data.py` — review `get_or_create` key fix (no other logic touched).
- `server/build.sh` — seed errors are loud; migrate still precedes seeding.
- `.github/workflows/ci-cd.yml` — renamed `CI Pipeline`; `validate-deployment` job is honest validation, no fake success.
- `DEPLOYMENT_INSTRUCTIONS.md` — rewritten to Blueprint reality (steps, env table, seed/admin/verify/troubleshoot/manual checklist).
- `render.yaml` — **unchanged** (verified correct: root Blueprint, 3.11.0 == `runtime.txt`, repo-root buildCommand with `cd`-safe script, frontend build → `collectstatic` → `migrate` → seed, gunicorn `$PORT` bind, `/` health check 200 in both modes, `DATABASE_URL` linkage, explicit `ALLOWED_HOSTS`, proxy-derived HTTPS settings).

## 3. Actual test results (all run locally 2026-10-13)

- `manage.py check` → no issues; `makemigrations --check --dry-run` → no changes
- `manage.py test` → **OK, 27/27** (21 prior + 6 new)
- `check --deploy` (prod-like env, 50+ char key) → only W004 HSTS advisory
- Prod-guard probes → `ImproperlyConfigured` for missing `SECRET_KEY`, missing `ALLOWED_HOSTS`, wildcard hosts (all confirmed)
- flake8 `djangoapp djangoproj` (E9,F63,F7,F82) → clean; `bash -n build.sh` → OK; `render.yaml` + workflow YAML parse → valid
- `populate_data` ×2 on dev DB → counts stable (4 dealers / 4 reviews / 6 users)
- `npm run build` → "build folder ready" (1 pre-existing exhaustive-deps warning)
- Live re-verify post-change → login 200, `/api/user/` true, review POST 201 + persisted (temp review deleted afterwards)
- `git diff --check` → clean (see below)

## 4. Remaining blockers (require a real deploy)

1. Remote deployment itself — nothing here substitutes for it.
2. Runtime-only risks in §1 #11 (worker memory, health-check/redirect interplay, free-DB retention).
3. `deploymentURL` still names a URL that returns 404; update only after a verified deploy.
4. No `deployed_*.png` — capture only against the live URL.

## 5. Required Render dashboard actions (owner)

Apply Blueprint → confirm generated `SECRET_KEY`/`DATABASE_URL` → fix hostnames if renamed →
`createsuperuser` + verify homepage/API/auth/review/admin/static pages per
`DEPLOYMENT_INSTRUCTIONS.md` §5 → update `deploymentURL` → capture `deployed_*.png`.

## 6. Exact local commands

```bash
cd /home/parag/Projects/car-dealership-portal/server
./.venv/bin/python manage.py check
DEBUG=False SECRET_KEY=<50+chars> ALLOWED_HOSTS=example.com ./.venv/bin/python manage.py check --deploy
./.venv/bin/python manage.py makemigrations --check --dry-run
./.venv/bin/python manage.py test
./.venv/bin/python -m flake8 djangoapp djangoproj --count --select=E9,F63,F7,F82 --show-source --statistics
bash -n build.sh
cd frontend && npm run build
```

## 7. Production deployment verified?

**No.** Configuration is locally verified; deployment needs the owner actions in §5.
