# Rubric Audit — Car Dealership Portal

**Audit date (UTC):** 2026-10-13
**Audited commit:** `45e598d` plus uncommitted working-tree fixes (see `git status` / `git diff`)
**Environment:** local dev — Django 4.2.7 + DRF 3.14 (`server/.venv`, Python 3.14.8), React 18 dev server on `:3000` proxied to Django on `:8000`, SQLite with `populate_data` sample data.
**Rule followed:** nothing marked complete on claims alone — every PASS below has a cited test or screenshot.

## Pre-existing working-tree changes (preserved, not redone)

- `server/requirements.txt`: `psycopg2-binary` 2.9.9 → 2.9.11 — kept.
- `server/djangoproj/settings.py`: `STATICFILES_DIRS` filters to existing dirs — kept.
- `server/djangoapp/views.py`: `CsrfExemptSessionAuthentication` on session-auth API views; empty-string normalization for optional review fields — kept.
- `server/djangoproj/urls.py`: homepage fallback to JSON status when React build missing — kept.
- `server/frontend/src/components/Home/Home.jsx`: CSS import `../Dealers/Dealers.css` — kept.

## Requirement mapping

| # | Rubric requirement | Source files / route | Status | Evidence (actual test) | Fix required |
|---|---|---|---|---|---|
| 1 | README with project details | `README.md` | PASS | Exists; install/API/admin sections accurate for local dev | None |
| 2 | Django server runs | `server/manage.py`, `djangoproj/settings.py` | PASS | `manage.py check` clean; `runserver :8000` served all routes below | None |
| 3 | About Us page | `server/frontend/static/About.html` → `/static/About.html` | PASS | `screenshots/about_us.png`: gradient styling, 3 team members, roles, emails | None |
| 4 | Contact Us page | `server/frontend/static/Contact.html` → `/static/Contact.html` | PASS (after fix) | Before fix it rendered unstyled with 404 CSS/images; rewritten to match About design. `screenshots/contact_us.png` | **Fixed 2026-10-13:** removed dead `/static/bootstrap.min.css`, `/static/style.css`, `/static/contactus.png`, `/static/cars.jpeg` refs; Bootstrap CDN + inline styles; same navbar; info cards; form; map block |
| 5 | Login API | `djangoapp/views.py::login_user`, `/api/login/` | PASS | `AuthAPITestCase.test_login_logout_current_user_cycle`; live curl 200 + `{"message":"Login successful"}`; bad creds → 401 (test + live) | None |
| 6 | Logout API | `djangoapp/views.py::logout_user`, `/api/logout/` | PASS | Test + live: 200 `{"message":"Logout successful"}`, subsequent `/api/user/` → `authenticated:false` | None |
| 7 | Sign-up page + register API | `frontend/src/components/Register/Register.jsx`, `/api/register/` | PASS | `test_register_creates_and_logs_in_user` (201 + session set); duplicate username → 400; live curl 201 | None |
| 8 | Get dealer reviews | `get_dealer_reviews`, `/api/reviews/dealer/<id>/` | PASS | `ReviewAPITestCase` GET empty→POST→GET persisted; unknown dealer → 404 (test + live) | None |
| 9 | Get all dealers | `get_dealers`, `/api/dealers/` | PASS | `DealerAPITestCase.test_get_all_dealers`; `screenshots/get_dealers.png` shows HTTP 200 DRF JSON | None |
| 10 | Get dealer by ID | `get_dealer_by_id`, `/api/dealers/<id>/` | PASS | Test 200 + 404 case; live 200 | None |
| 11 | Get dealers by state | `get_dealers_by_state`, `/api/dealers/state/<state>/` | PASS | Tests incl. case-insensitive `kansas`; `screenshots/dealersbystate.png` shows only Kansas dealers | None |
| 12 | Admin login | `django.contrib.admin`, `/admin/` | PASS | `screenshots/admin_login.png`: logged in as `screenshot_admin`, models visible (Car makes/models, Dealers, Reviews) | None (dedicated local superuser created via management shell) |
| 13 | Admin logout | `/admin/logout/` | PASS | `screenshots/admin_logout.png`: "Logged out / Thanks for spending some quality time…" | None |
| 14/15 | Car makes & models | `get_car_makes`, `get_car_models`, `/api/cars/makes/`, `/api/cars/models/` | PASS | `CarAndSentimentAPITestCase` live-data assertions; curl 200 | None |
| 16 | Sentiment analysis | `analyze_review_sentiment`, `/api/analyze/` | PASS | Tests positive/negative/neutral + empty-text 400; live `{"text":"Fantastic services","sentiment":"positive"}` | None |
| 17 | Home dealers (logged out) | `Home.jsx`, `/` | PASS | `screenshots/homepage.png`: 4 dealer cards, counts, View Details, state filter, no Review buttons | None |
| 18 | Home dealers (logged in) | `Home.jsx` + `Navigation.jsx`, `/api/user/` | PASS | `screenshots/get_dealers_loggedin.png`: "Welcome, testuser", Logout, Review Dealer buttons | None |
| 19 | Filter by state (UI) | `Home.jsx::handleStateFilter` | PASS | `screenshots/dealersbystate.png`: filter=Kansas, 2 Kansas dealers only | None |
| 20 | Dealer details + reviews | `DealerDetails.jsx`, `/dealer/:id` | PASS | `screenshots/dealer_id_reviews.png`: address/city/state/zip/phone/email/website/desc, 2 reviews, sentiment badges, Write a Review | None |
| 21 | Post-review form | `PostReview.jsx`, `/postreview/:id` | PASS | `screenshots/dealership_review_submission.png`: filled textarea, purchase checkbox, date/make/model/year, Submit/Cancel | None |
| 22 | Posted review appears | POST `/api/reviews/` → redirect `/dealer/:id` | PASS | `screenshots/added_review.png`: Customer Reviews (2→3), testuser review on top, positive badge, purchase line | None |
| 23 | CI/CD workflow | `.github/workflows/ci-cd.yml` | PASS (after fix) | Deploy job was placeholder echoes incl. false "Deployment completed successfully!". Replaced with real validation (render.yaml parse, `bash -n build.sh`, `manage.py check`) + honest manual-deploy note. Validated locally | **Fixed 2026-10-13** |
| 24 | Deployment URL | `deploymentURL` | NOT VERIFIED | File claims `https://car-dealership-portal.onrender.com`; live curl returns **404 "Not Found"**. No remote deploy performed (needs owner action) | Owner must deploy via Render dashboard per `DEPLOYMENT_INSTRUCTIONS.md`, then update file |
| 25–28 | Deployed landing / logged-in / dealer detail / review | (remote only) | NOT VERIFIED | Blocked by #24 — no `deployed_*.png` captured; capturing them against a dead URL would be fabrication | Same as #24 |
| — | Current-user state | `get_current_user`, `/api/user/` | PASS | Tests + live true/false cycle | None |
| — | Unauthenticated review POST rejected | `post_review` (`IsAuthenticated`) | PASS | Test + live 403; security middleware/CSRF globally intact (exemption only on the documented API views, verified in `views.py`) | None |
| — | Review validation / negative paths | `ReviewSerializer` + views | PASS | Missing text → 400; unknown dealer → 404; empty optional fields accepted (regression test for the `''` normalization) | None |
| — | Migrations / system check | `djangoapp/migrations/` | PASS | `makemigrations --check` → "No changes detected"; `check` clean | None |
| — | Frontend production build | `server/frontend`, `build/` | PASS | `npm run build` → "The build folder is ready to be deployed" (1 pre-existing exhaustive-deps warning in `PostReview.jsx`) | None |
| — | `render.yaml` build path | `render.yaml` + `server/build.sh` | PASS (after fix) | `build.sh` assumed CWD=`server/` but Render runs it from repo root → `pip install -r requirements.txt` / `manage.py` would fail; also never built the React frontend the Django homepage serves. Fixed with `cd "$(dirname "$0")"` + guarded frontend build. `bash -n` + YAML parse verified | **Fixed 2026-10-13** |

## Genuine defects found and fixed in this pass

1. `Contact.html` referenced non-existent `/static/bootstrap.min.css`, `/static/style.css`, `/static/contactus.png`, `/static/cars.jpeg` — rendered unstyled. Rewritten to the About-page pattern (CDN + inline CSS, no local assets).
2. CI `deploy` job printed fake success without deploying — replaced with config validation + honest manual-step note.
3. `build.sh` would fail on Render (wrong CWD, no frontend build) — fixed.
4. Test coverage was 3 model-only tests — added 18 API tests (auth cycle, dealers incl. 404/case-insensitivity, review persistence/validation/auth, cars, sentiment incl. negative paths). Suite: **21/21 pass**.

## Intentionally not changed

- Global CSRF/CORS/security settings — exemptions remain scoped to the API views; public vs session-authenticated behavior verified (200s public GETs, 403 unauth POST, 401 bad login).
- No hardcoded success responses or mocked-data tests — all tests hit real ORM/DRF code paths.
- No remote deploy, no secrets committed, no production data touched.
