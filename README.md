# Movie Night

Movie Night is a small web application for dorm residents to organize movie screenings together.

The project consists of:
- **FastAPI** backend for business logic and REST API
- **SQLite** database for persistent storage
- **Streamlit** frontend for manual use and exploratory testing
- **JWT authentication** with password hashing via `pwdlib` using the default Argon2id configuration

The application supports:
- user login, registration, logout, and token validation
- creating movie screening proposals
- grouping same-room overlapping proposals into conflict pairs
- voting inside a conflict pair
- automatic winner selection when voting closes
- snack reaction management for the final selected screening
- a catalog view for browsing all proposals
- a weekly room schedule built on fixed 2-hour slots

The project follows the SQR group project stack and quality-gate approach, where Poetry is part of the expected environment, and the backend/frontend stack is FastAPI + SQLite + Streamlit. The PM quality plan for Movie Night also fixes the required gates around flake8, bandit, coverage, radon, and endpoint documentation.

---

## 1. Main idea

Users propose screenings in dorm rooms. Each proposal contains:
- room
- movie title
- start time
- end time
- author

If two proposals overlap in the same room, they form a **conflict pair**. Users can vote for one option inside that pair. Because the UI uses fixed 2-hour slot starts, the practical model is pairwise competition between proposal **A** and proposal **B** inside the same room and slot window; chained overlap scenarios like `A overlaps B` and `B overlaps C` are not part of the current product behavior. When the start time is close enough, the system determines the winner.

Snack reactions are treated separately from voting. They do not influence the winner. They become available only during the final hour before the event, and in conflict situations only the selected winner can receive reactions. Hidden reaction data is not exposed by the API before it becomes visible.

---

## 2. Tech stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite
- Pydantic / pydantic-settings
- PyJWT
- pwdlib

### Frontend
- Streamlit
- requests

### Tooling
- Poetry
- pytest / pytest-cov
- flake8
- bandit
- radon
- locust
- pre-commit

---

## 3. Repository layout

```text
.
├── src/movienight/
│   ├── api/                 # FastAPI routers and dependencies
│   ├── core/                # config, clock, security, slot helpers
│   ├── db/                  # SQLAlchemy base, models, session, DB init
│   ├── integrations/        # external integration adapters (movie provider stub)
│   ├── repositories/        # DB access layer
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # business logic
│   └── main.py              # FastAPI application entrypoint
├── streamlit_app/
│   ├── frontend/            # Streamlit API client, shared components, state
│   ├── pages/               # multipage Streamlit UI
│   └── app.py               # overview page
├── tests/                   # test skeletons
├── .github/workflows/ci.yml # CI pipeline
├── .pre-commit-config.yaml  # local quality gates
├── load_tests.py            # locust entrypoint
├── pyproject.toml           # Poetry configuration
├── requirements.txt         # direct pip requirements
└── .env.example            # environment variables example
```

---

## 4. Environment variables

Create `.env` from the template:

```bash
cp .env.example .env
```

Default template:

```env
APP_NAME=Movie Night
APP_ENV=dev
APP_DEBUG=true
DATABASE_URL=sqlite:///./movie_night.db
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120

BOOTSTRAP_USERNAME=admin
BOOTSTRAP_PASSWORD=P@ssw0rd123
```

### What these variables do
- `DATABASE_URL` — SQLite database path
- `JWT_SECRET` — signing secret for JWT access tokens
- `JWT_ALGORITHM` — signing algorithm
- `JWT_EXPIRE_MINUTES` — token lifetime
- `BOOTSTRAP_USERNAME` / `BOOTSTRAP_PASSWORD` — first account created automatically when DB is empty

---

## 5. Installation

### Option A. Poetry

From the project root:

```bash
poetry install
```

If your local Poetry environment does not yet contain Streamlit runtime packages for the frontend, add them once:

```bash
poetry add streamlit requests
```

### Option B. pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

---

## 6. Run the project

### Terminal 1 — backend

```bash
poetry run uvicorn --app-dir src movienight.main:app --reload
```

Backend URLs:
- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Terminal 2 — frontend

```bash
poetry run streamlit run streamlit_app/app.py
```

Frontend URL:
- `http://localhost:8501`

---

## 7. First launch notes

On startup the backend runs database initialization.

If the database is empty:
- all tables are created
- one bootstrap user is inserted using `BOOTSTRAP_USERNAME` and `BOOTSTRAP_PASSWORD`

If you want a clean restart:

```bash
rm -f movie_night.db
```

Then start the backend again.

---

## 8. Authentication flow

1. Open the Streamlit app.
2. Go to **Login / Registration**.
3. Sign in with the bootstrap account from `.env`, or create a new account.
4. After login, the frontend stores the JWT token in Streamlit session state.
5. All protected API calls send `Authorization: Bearer <token>` automatically.
6. Logout revokes the current token on the backend.

---

## 9. Feature overview

### 9.1 Authentication
- login
- registration
- logout with token revocation
- get current user (`/auth/me`)

### 9.2 Proposals
- create a screening proposal
- delete your own proposal
- prevent invalid schedules
- prevent invalid overlapping duplicates

### 9.3 Voting
- one user can vote once inside one conflict group
- users cannot vote for their own proposal
- voting is locked when the proposal is in the past or starts within one hour

### 9.4 Snack reactions
- categories: pizza, popcorn, burger, sushi, drinks
- a user can add multiple categories
- the same category cannot be added twice by the same user to the same proposal
- reactions are available only during the final hour before start
- if two proposals are in conflict, reactions are allowed only for the selected winner
- when reactions are not visible yet, the API does not expose hidden reaction counts

### 9.5 Conflict pairs
- proposals in the same room that overlap in time are handled as conflict pairs
- with the current fixed 2-hour slot model, chained overlap cases like `A-B-C` are not expected product behavior
- voting is performed per conflicting pair, not globally
- when voting closes, the winner is selected

### 9.6 Card Catalog
- browses all proposals visually
- current proposal is centered
- adjacent proposals are shown as clickable background cards

### 9.7 Weekly schedule
- backend exposes a weekly room schedule
- rooms are shown with fixed 2-hour slots
- create form uses a 2-hour slot start selector on the frontend

---

## 10. API summary

### System
- `GET /` — root status
- `GET /health` — health check

### Auth
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Main data
- `GET /api/v1/home` — grouped proposals for main page
- `GET /api/v1/catalog` — grouped proposals for catalog view
- `GET /api/v1/schedule` — weekly room schedule

### Proposal lifecycle
- `POST /api/v1/proposals`
- `DELETE /api/v1/proposals/{proposal_id}`

`POST /api/v1/proposals` may return **400 Bad Request** when proposal creation violates business rules, for example:
- start time is in the past
- end time is not later than start time
- duration is not exactly 2 hours
- start time is not aligned to a 2-hour slot boundary
- overlapping proposal with the same room and movie already exists
- there are already 5 overlapping proposals in the same room
- a conflicting proposal is being created within the last hour before start

### Votes
- `POST /api/v1/proposals/{proposal_id}/votes`
- `DELETE /api/v1/proposals/{proposal_id}/votes`

### Snack reactions
- `POST /api/v1/proposals/{proposal_id}/reactions`
- `DELETE /api/v1/proposals/{proposal_id}/reactions/{category}`

See `/docs` for full OpenAPI models.

---

## 11. Quality gates

### Pre-commit

```bash
poetry run flake8 src/ --count --select=E,F,W --show-source --statistics
poetry run bandit -r src/ -ll
```

### PR / CI checks

```bash
poetry run flake8 src/ --count --select=E,F,W --show-source --statistics
poetry run bandit -r src/ -ll
poetry run pytest --cov=src --cov-fail-under=70
poetry run radon cc -a -s src/
poetry run radon mi -s src/
poetry run locust -f load_tests.py --headless -u 10 -r 2 --run-time 1m
```

The repository already contains:
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

### Important note
At the moment, the test suite in the archive is still mostly placeholder-level and needs to be expanded to satisfy the real reliability goals.

---

## 12. Manual smoke test

### Login
- start backend
- start frontend
- login as bootstrap user

### Create proposals
- create proposal A in Room A
- create overlapping proposal B in Room A
- verify they appear as one conflict group on Home

### Vote
- log in as another user
- vote for one proposal
- verify that a second vote in the same group is blocked

### Reactions
- wait until the proposal enters the final hour before start
- if there is a conflict pair, verify reactions are allowed only for the selected winner
- verify duplicate category is blocked

### Delete
- delete your own future proposal
- verify past proposals cannot be deleted

---

## 13. Known limitations / current status

- `integrations/movie_provider.py` is currently a stub and not wired into the user flow yet
- tests in `tests/` are scaffolding and should be replaced with real coverage-driving tests
- the frontend is intentionally simple and optimized for manual testing rather than polished production UX
- the current conflict model is intentionally pairwise under fixed 2-hour slots; chain-overlap scenarios are out of scope for the implemented product behavior

---

## 14. Authors / course context

This repository is part of the SQR group project assignment for Spring 2026, using the required simple stack with Poetry, FastAPI, SQLite, Streamlit, and automated quality gates. The Movie Night PM quality plan focuses especially on reliable scheduling and voting behavior.