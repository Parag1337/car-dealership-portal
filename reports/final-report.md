# Final Report — Car Dealership Portal audit, repair, testing, screenshots

**Date (UTC):** 2026-10-13
**Repo:** `https://github.com/Parag1337/car-dealership-portal` (work done in local clone; **nothing committed or pushed** — all changes are in the working tree for owner review)

## 1. Features verified as passing (with evidence)

- Homepage + dealer listings, logged-out and logged-in states (`homepage.png`, `get_dealers_loggedin.png`)
- Dealer detail with reviews + sentiment badges (`dealer_id_reviews.png`)
- State filtering via API (incl. case-insensitive) and UI (`dealersbystate.png`)
- Registration (201 + auto-login, duplicate rejected), login/logout/current-user cycle, bad-credentials 401
- Review submission, persistence, display, purchase details; unauthenticated POST → 403; missing text → 400; unknown dealer → 404
- Car makes/models endpoints; sentiment positive/negative/neutral + empty-text 400
- Django admin login/logout (`admin_login.png`, `admin_logout.png`)
- About Us and Contact Us pages (`about_us.png`, `contact_us.png`)
- `manage.py check` clean, `makemigrations --check` no changes, frontend `npm run build` succeeds

## 2. Features fixed in this pass

1. **`server/frontend/static/Contact.html`** — was rendering completely unstyled (dead refs to `/static/bootstrap.min.css`, `/static/style.css`, missing images). Rewritten to match the About-page design (Bootstrap CDN, gradient, info cards, form, map block). Re-screenshotted.
2. **`server/djangoapp/tests.py`** — was 3 model-only tests. Added 18 API tests: `AuthAPITestCase` (5), `DealerAPITestCase` (5), `ReviewAPITestCase` (4), `CarAndSentimentAPITestCase` (4).
3. **`.github/workflows/ci-cd.yml`** — `deploy` job only echoed placeholder text including a false "Deployment completed successfully!". Now runs real validation (`render.yaml` parse, `bash -n build.sh`, `manage.py check`) and states that remote deploy needs manual dashboard setup.
4. **`server/build.sh`** — assumed CWD=`server/` (Render runs it from repo root, so `pip install -r requirements.txt` and `manage.py` would fail) and never built the React frontend that Django serves. Added `cd "$(dirname "$0")"` and a guarded `npm install && npm run build` step.

## 3. Tests run and actual results

| Command (from `server/`, Python via `.venv/bin/python`) | Result |
|---|---|
| `manage.py check` | No issues |
| `manage.py makemigrations --check --dry-run` | No changes detected |
| `manage.py test` (21 tests: 3 pre-existing + 18 new) | **OK, 21/21 pass** |
| `npm run build` (from `server/frontend`) | Success, "build folder ready" (1 pre-existing exhaustive-deps warning in `PostReview.jsx:25`) |
| Live curl matrix vs `127.0.0.1:8000` (`/`, `/api/dealers/`, `/api/dealers/1/`, `/api/dealers/state/Kansas/`, `/api/reviews/dealer/1/`, `/api/cars/makes/`, `/api/cars/models/`, POST `/api/analyze/`, `/api/user/`, `/admin/login/`) | All 200; sentiment `{"text":"Fantastic services","sentiment":"positive"}` |
| Live auth cycle (register → user → post review → reviews → unauth 403 → bad-login 401 → logout → user false) | All as expected |
| Playwright real-browser flows (login UI, state filter, dealer page, review form fill + submit + redirect) | All behaved as designed; 11 genuine screenshots |
| CI-step validation (`render.yaml` + `ci-cd.yml` YAML parse, `bash -n build.sh`) | Valid |

## 4. Unresolved failures / blockers

- **Remote deployment NOT VERIFIED.** `deploymentURL` claims `https://car-dealership-portal.onrender.com`, but it returns **HTTP 404**. No `deployed_*.png` captured (capturing them would require fabrication). Blocked on owner action — see §8.
- Pre-existing React warning (`PostReview.jsx` exhaustive-deps) — cosmetic, left untouched.
- CI workflow remote run not observed (no push made without approval); steps were validated locally instead.

## 5. Screenshots (`screenshots/`, all real browser captures, no credentials shown)

- `screenshots/homepage.png` — home, logged out
- `screenshots/get_dealers.png` — live `GET /api/dealers/` JSON (HTTP 200, DRF browser view)
- `screenshots/get_dealers_loggedin.png` — home as `testuser` (Welcome + Logout + Review Dealer buttons)
- `screenshots/dealersbystate.png` — Kansas filter, 2 Kansas dealers only
- `screenshots/dealer_id_reviews.png` — Premier Auto Group + 2 reviews + sentiment badges + Write a Review
- `screenshots/dealership_review_submission.png` — filled review form (purchase + Toyota Camry 2023)
- `screenshots/added_review.png` — dealer page after posting (Reviews 2→3, testuser review on top)
- `screenshots/about_us.png`, `screenshots/contact_us.png` — static pages
- `screenshots/admin_login.png` — admin index as `screenshot_admin`; `screenshots/admin_logout.png` — "Logged out" confirmation
- `deployed_*.png` — **not captured** (no working deployment; see §4)

## 6. Deployment verification

**Not verified.** Neither a new deployment nor changes to remote settings/data were made (per instructions). The URL on file is dead (404).

## 7. Exact commands to start the app

```bash
# Backend (from repo root or server/)
cd /home/parag/Projects/car-dealership-portal/server
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py populate_data   # sample dealers/makes/models/users/reviews (idempotent)
./.venv/bin/python manage.py runserver 127.0.0.1:8000

# Frontend (separate terminal; documented :3000 + proxy setup)
cd /home/parag/Projects/car-dealership-portal/server/frontend
npm install   # first time only
npm start     # serves http://127.0.0.1:3000, proxies /api to :8000
```

Local test accounts (dev DB only, passwords not shown in any screenshot): `testuser` / sample-data password per `GRADING_CHECKLIST.md`; superuser `screenshot_admin` (staff+superuser, created for admin screenshots).
Admin: `http://127.0.0.1:8000/admin/` · API: `http://127.0.0.1:8000/api/dealers/` · About: `http://127.0.0.1:8000/static/About.html`

## 8. Manual steps still required (owner)

1. **Deploy:** connect the repo in the Render dashboard (blueprint: `render.yaml`; details in `DEPLOYMENT_INSTRUCTIONS.md`), add env vars (`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`), deploy, run `createsuperuser` + `populate_data` on the live service.
2. **Verify live:** hit `/`, `/api/dealers/`, `/dealer/1`, login, post a review; capture `deployed_landingpage.png`, `deployed_loggedin.png`, `deployed_dealer_detail.png`, `deployed_add_review.png` into `screenshots/`.
3. **Update files:** correct `deploymentURL` with the real live URL; then flip `GRADING_CHECKLIST.md` Tasks 24–28 from "Ready for Deployment" to verified.
4. **Review + commit:** inspect `git diff` (changed: `.github/workflows/ci-cd.yml`, `server/build.sh`, `server/djangoapp/tests.py`, `server/frontend/static/Contact.html`; new: `screenshots/`, `reports/`), then commit/push. Pre-existing uncommitted changes (`views.py`, `settings.py`, `urls.py`, `Home.jsx`, `requirements.txt`) were preserved untouched.
