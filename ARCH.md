# Movie Night — Architecture and Business Logic

This document explains the internal architecture, implemented business rules, feature behavior, and end-to-end user scenarios for the Movie Night project.

---

# 1. Purpose of the application

Movie Night is designed for dorm residents who want to coordinate movie screenings in shared rooms.

The application solves several problems at once:
- users need a simple way to propose a screening
- multiple users may propose different movies for the same room and overlapping time
- the system must prevent broken schedules
- users should be able to vote for one option in a conflict pair
- the system must choose a winner deterministically
- users want light social interaction around the final selected event through snack reactions

The application therefore combines:
- **authentication**
- **proposal scheduling**
- **conflict detection**
- **voting**
- **reaction tracking**
- **manual testing UI**

---

# 2. High-level architecture

The repository is split into two main runtime parts:

1. **Backend** — FastAPI application in `src/movienight/`
2. **Frontend** — Streamlit application in `streamlit_app/`

Both parts use the same backend API contract.

## 2.1 Backend layers

The backend is organized in classic application layers.

### API layer
Files:
- `src/movienight/api/router.py`
- `src/movienight/api/v1/*.py`
- `src/movienight/api/deps.py`

Responsibilities:
- define REST endpoints
- describe summary / description / response_model for OpenAPI
- resolve dependencies such as DB session and current user
- call service layer methods

### Service layer
Files:
- `src/movienight/services/*.py`

Responsibilities:
- implement business rules
- orchestrate repositories
- validate timing / voting / reaction constraints
- produce response-ready data structures

### Repository layer
Files:
- `src/movienight/repositories/*.py`

Responsibilities:
- encapsulate SQLAlchemy queries
- provide narrow data-access methods
- avoid mixing raw query logic into services

### Schema layer
Files:
- `src/movienight/schemas/*.py`

Responsibilities:
- request validation
- response serialization
- explicit API contract for frontend and Swagger docs

### Core layer
Files:
- `src/movienight/core/*.py`

Responsibilities:
- application settings
- time helpers
- JWT/password security
- slot helper utilities

### Database layer
Files:
- `src/movienight/db/*.py`

Responsibilities:
- SQLAlchemy base and session
- ORM models
- startup initialization
- bootstrap user insertion

---

# 3. Backend entrypoint

## File
`src/movienight/main.py`

## Responsibilities
- create FastAPI app
- configure CORS for local frontend/backend URLs
- include versioned API router under `/api/v1`
- expose `/`, `/health`, `/docs`, `/redoc`
- initialize DB on startup

This means the backend is self-initializing for local development.

---

# 4. Configuration model

## File
`src/movienight/core/config.py`

The application reads configuration from `.env` using `pydantic-settings`.

### Main settings
- `APP_NAME`
- `APP_ENV`
- `APP_DEBUG`
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`
- `BOOTSTRAP_USERNAME`
- `BOOTSTRAP_PASSWORD`

### Why bootstrap credentials exist
The project needs a clean first-login path after the first launch. Therefore the DB initializer creates exactly one initial user if the users table is empty.

---

# 5. Persistence model

## File
`src/movienight/db/models.py`

The application uses five core persistence entities.

## 5.1 User
Fields:
- `id`
- `username`
- `password_hash`
- `created_at`

Used for:
- authentication
- proposal ownership
- vote ownership
- reaction ownership

## 5.2 Proposal
Fields:
- `id`
- `creator_id`
- `room`
- `movie_title`
- `starts_at`
- `ends_at`
- `created_at`

Represents one movie screening proposal.

## 5.3 Vote
Fields:
- `id`
- `user_id`
- `proposal_id`
- `created_at`

Unique constraint:
- one user cannot create duplicate votes for the same proposal

## 5.4 FoodReaction
Fields:
- `id`
- `user_id`
- `proposal_id`
- `category`
- `created_at`

Unique constraint:
- one user cannot add the same reaction category twice to the same proposal

## 5.5 RevokedToken
Fields:
- `id`
- `jti`
- `expires_at`
- `reason`

Used to implement logout by invalidating current JWTs.

---

# 6. Authentication architecture

## Files
- `src/movienight/api/v1/auth.py`
- `src/movienight/services/auth_service.py`
- `src/movienight/core/security.py`
- `src/movienight/api/deps.py`
- `src/movienight/repositories/users.py`
- `src/movienight/repositories/revoked_tokens.py`

## 6.1 Password handling
Passwords are hashed using `pwdlib` with the default Argon2id configuration.

This gives:
- strong password hashing
- no plaintext password storage
- simple verification workflow

## 6.2 JWT flow
### Login
`POST /api/v1/auth/login`
- user sends username + password
- service checks if the caller is already authenticated
- service validates password hash
- service returns JWT access token and user payload

### Register
`POST /api/v1/auth/register`
- only anonymous users can register
- username uniqueness is enforced
- password is hashed before storage
- the response returns a JWT immediately after account creation

### Current user
`GET /api/v1/auth/me`
- validates JWT
- resolves authenticated user
- returns user payload

### Logout
`POST /api/v1/auth/logout`
- parses token claims
- extracts `jti` and expiration
- stores `jti` in `revoked_tokens`
- future requests with the same token can be rejected

## 6.3 Dependency resolution
`get_current_user` protects private endpoints.

`get_optional_current_user` is used where behavior changes depending on whether the caller is already authenticated, such as login/register.

---

# 7. Proposal creation logic

## Files
- `src/movienight/api/v1/proposals.py`
- `src/movienight/services/proposal_service.py`
- `src/movienight/services/schedule_rules.py`
- `src/movienight/repositories/proposals.py`
- `src/movienight/schemas/proposal.py`

## 7.1 Input model
A proposal contains:
- room
- movie title
- starts_at
- ends_at

## 7.2 Timing validation
The current implementation enforces fixed 2-hour slots.

A proposal is rejected with **400 Bad Request** if:
- start is in the past
- end is not after start
- duration is not exactly 2 hours
- start time is not aligned to a 2-hour boundary (`00:00`, `02:00`, `04:00`, ...)

This is stricter than the original free-form version but simplifies schedule consistency.

## 7.3 Conflict validation
The system loads existing proposals for the same room and evaluates overlaps.

A proposal is rejected if:
- the same room + same movie already exists with overlapping time
- there are already 5 or more overlaps for the requested time in that room
- the new proposal conflicts with existing proposals and starts in one hour or less

## 7.4 Successful creation flow
If all checks pass:
- proposal is persisted
- `created_at` is set to current UTC
- created proposal is returned as API response

---

# 8. Proposal deletion logic

## Files
- `src/movienight/services/proposal_service.py`
- `src/movienight/services/schedule_rules.py`

A proposal can be deleted only when:
- it exists
- it belongs to the current user
- it has not started in the past

The application does not persist “winner” state separately. Winner is recalculated dynamically from the remaining proposals in a conflict group, so deleting a proposal implicitly changes future group resolution if needed.

---

# 9. Conflict-pair model

## File
`src/movienight/services/voting_rules.py`

The application does not treat conflicting proposals as a free-form graph anymore from a product perspective.

Instead, under the current fixed 2-hour slot model, practical conflicts are handled as **pairwise conflicts in the same room and slot window**:
- proposal **A** may conflict with proposal **B**
- users vote between the alternatives visible in that single conflicting slot
- chained overlap scenarios like `A overlaps B` and `B overlaps C` are not part of the intended product behavior

This is important because the documentation and UI now describe the feature as pairwise voting between competing proposals for the same screening slot, not as arbitrary overlap-component traversal.

---

# 10. Voting logic

## Files
- `src/movienight/api/v1/votes.py`
- `src/movienight/services/vote_service.py`
- `src/movienight/services/voting_rules.py`
- `src/movienight/repositories/votes.py`

## 10.1 Voting rules
A user can add a vote only if:
- proposal exists
- proposal does not belong to the same user
- proposal is not in the past
- proposal does not start within one hour
- the user has not already voted for this proposal
- the user has not already voted for any other proposal in the same conflict group

## 10.2 Vote removal rules
A vote can be removed only if:
- the vote exists for this user and proposal
- proposal is not in the past
- proposal does not start within one hour

## 10.3 Why votes are group-scoped
The product logic models a conflict group as a mini election. A user must choose one option among conflicting screenings, not stack votes across all overlapping options.

---

# 11. Winner selection logic

## Files
- `src/movienight/services/home_service.py`
- `src/movienight/services/voting_rules.py`

Winner selection is dynamic.

For each conflict pair:
1. count votes for every proposal
2. sort by:
   - highest vote count first
   - earliest creation time first
   - lowest id as final stabilizer
3. choose the first proposal as winner

## Important visibility rule
The winner is exposed in API responses only when:
- the slot is actually a conflict pair
- the voting window is already locked (`start <= now + 1 hour`)

Before that moment, the group is still “open” and the UI treats it as an active vote.

---

# 12. Reaction logic

## Files
- `src/movienight/api/v1/reactions.py`
- `src/movienight/services/reaction_service.py`
- `src/movienight/services/voting_rules.py`
- `src/movienight/repositories/reactions.py`

## 12.1 Supported categories
Defined in `FoodCategory`:
- pizza
- popcorn
- burger
- sushi
- drinks

## 12.2 Add reaction rules
A reaction can be added only if:
- proposal exists
- proposal is not in the past
- the proposal is currently the valid **reaction target**
- the same category is not already set by the same user on the same proposal

The reaction target rule is:
- for a single proposal with no conflict, the proposal becomes reaction-enabled during the final hour before start
- for a conflict pair, only the selected winner becomes reaction-enabled during the final hour before start

## 12.3 Remove reaction rules
A reaction can be removed only if:
- proposal exists
- proposal is not in the past
- the proposal is currently the valid reaction target
- that specific category was previously set by the same user

## 12.4 Visibility rule
The backend no longer sends hidden reaction data.

The backend computes `show_reactions` as a real feature-availability flag:
- `show_reactions = false` means this proposal is not the current reaction target and reaction counts are not exposed
- `show_reactions = true` means the proposal is the current reaction target and reaction data can be shown honestly

As a result:
- hidden reaction counts are not leaked through the API
- the frontend does not render the reaction selector for non-target proposals
- in a conflict pair, reactions belong only to the winner during the final hour before start

---

# 13. Home page data aggregation

## Files
- `src/movienight/api/v1/home.py`
- `src/movienight/services/home_service.py`
- `src/movienight/schemas/home.py`

The Home endpoint is not a raw list of proposals.

It is a computed read model that aggregates:
- grouped proposals
- conflict metadata
- vote counts
- reaction counts only when they are actually visible
- current user’s vote flags
- current user’s reaction flags only for the current reaction target
- winner visibility
- allowed actions for the current user

## 13.1 Why this design is useful
Instead of making the frontend reimplement business rules, the backend sends explicit booleans:
- `can_vote`
- `can_unvote`
- `can_delete`
- `can_add_reaction`
- `can_remove_reaction`
- `show_reactions`
- `is_winner`
- `is_past`

This reduces frontend logic and keeps rule enforcement centralized.

---

# 14. Catalog endpoint

## File
`src/movienight/api/v1/catalog.py`

The catalog uses the same grouped-proposal model as Home but is intended for browsing all proposals in a card-based UI.

It currently calls the same home service with `mine_only=False`, so both Home and Catalog are backed by the same aggregation logic.

The difference is in presentation, not business rules.

---

# 15. Weekly schedule endpoint

## Files
- `src/movienight/api/v1/schedule.py`
- `src/movienight/services/schedule_service.py`
- `src/movienight/core/slots.py`
- `src/movienight/schemas/schedule.py`

The schedule endpoint produces a weekly room timetable.

## 15.1 How schedule is built
1. determine current week bounds
2. generate all fixed 2-hour slots for 7 days
3. repeat this for each room
4. match proposals to slots by overlap
5. produce structured response with:
   - room
   - day label
   - time label
   - proposal titles occupying that slot
   - proposal count
   - `is_past`
   - `is_locked`

## 15.2 Why it exists
This endpoint supports:
- schedule visualization
- creation form slot selection
- manual schedule inspection in frontend

---

# 16. Frontend architecture

## Main files
- `streamlit_app/app.py`
- `streamlit_app/frontend/api.py`
- `streamlit_app/frontend/components.py`
- `streamlit_app/frontend/state.py`
- `streamlit_app/pages/*.py`

## 16.1 Frontend state
State is stored in `st.session_state`.

Main keys:
- `api_base`
- `access_token`
- `current_user`
- `flash`
- `catalog_index`

## 16.2 API client
`frontend/api.py` is a thin wrapper over `requests`.

Responsibilities:
- build API URL from configured base
- attach JWT header
- normalize backend errors into `ApiError`
- clear auth state on 401
- expose helper functions such as `login()`, `get_home()`, `create_proposal()`

## 16.3 Shared UI helpers
`frontend/components.py` contains:
- app shell initialization
- sidebar rendering
- auth guard
- flash messages
- group rendering
- proposal card rendering
- reaction block rendering

This keeps page files small and avoids duplicating UI logic.

---

# 17. Streamlit pages

## 17.1 Overview page
File: `streamlit_app/app.py`

Purpose:
- quick project entry screen
- links to all major pages
- session status information

## 17.2 Login / Registration
File: `streamlit_app/pages/1_Login.py`

Features:
- login tab
- registration tab
- auto-redirect to Home after success
- block re-login when already authenticated

## 17.3 Home
File: `streamlit_app/pages/2_Home.py`

Purpose:
- render grouped proposals returned by `/api/v1/home`
- show conflicting alternatives for the same room/slot and the selected winner when voting closes
- allow vote/unvote/delete/reaction operations according to flags from backend

## 17.4 Create Proposal
File: `streamlit_app/pages/3_Create_Proposal.py`

Purpose:
- create proposal using a date picker plus 2-hour slot start selector
- automatically derive end time as `start + 2h`

## 17.5 Profile
File: `streamlit_app/pages/4_Profile.py`

Purpose:
- inspect current authenticated user
- inspect current token
- refresh `/auth/me`
- logout
- verify backend connectivity manually

## 17.6 Card Catalog
File: `streamlit_app/pages/5_Card_Catalog.py`

Purpose:
- browse proposals as cards
- center current card
- use left/right preview cards for navigation
- persist current index in session state

This page is intentionally UI-heavy and optimized for manual exploratory usage.

---

# 18. Detailed user scenarios

## Scenario 1. First launch and bootstrap login
1. User starts backend.
2. DB tables are created automatically.
3. If users table is empty, bootstrap user is created from `.env`.
4. User opens Streamlit frontend.
5. User goes to Login page.
6. User signs in with bootstrap credentials.
7. JWT is stored in session state.
8. User is redirected to Home.

## Scenario 2. User registration
1. Anonymous user opens Login / Registration page.
2. User fills new username and password twice.
3. Frontend checks that passwords match.
4. Backend checks that caller is anonymous.
5. Backend checks username uniqueness.
6. Backend stores new user with Argon2id hash.
7. Backend returns access token immediately.
8. Frontend stores token and redirects to Home.

## Scenario 3. Creating a valid proposal
1. Authenticated user opens Create Proposal page.
2. User selects room.
3. User enters movie title.
4. User selects date.
5. User selects start time from the 2-hour slot dropdown.
6. Frontend computes `ends_at = starts_at + 2 hours`.
7. Backend validates timing and conflicts. Invalid input returns **400 Bad Request** with a business-rule message.
8. Proposal is created.
9. User is redirected to Home.

## Scenario 4. Attempting invalid creation
Possible rejections:
- start in the past
- invalid end <= start
- duration not equal to 2 hours
- start not aligned to 2-hour boundary
- same room + same movie + overlap exists
- too many overlaps already exist
- conflicting proposal is created too close to start time

## Scenario 5. Two users create conflicting proposals
1. User A creates proposal in Room A for a valid 2-hour slot.
2. User B creates another proposal in the same room for the same conflicting time window.
3. Home shows both as competing alternatives for that screening slot.
4. Until one hour before start, the pair is open for voting.
5. When the pair locks, the winner is exposed.

## Scenario 6. Voting inside conflict group
1. User C opens Home.
2. User C sees two proposals inside one group.
3. User C votes for one option.
4. Backend records the vote.
5. User C attempts to vote for the second option in the same group.
6. Backend rejects it.

## Scenario 7. Vote cancellation
1. User C has an existing vote.
2. If event is still more than one hour away, user can cancel vote.
3. After lock window begins, cancellation is rejected.

## Scenario 8. Snack reactions
1. User opens Home or Catalog near the start time.
2. If the slot has no conflict, the single proposal becomes reaction-enabled during the final hour.
3. If the slot has a conflict, only the selected winner becomes reaction-enabled during the final hour.
4. Non-target proposals do not expose hidden reaction data and do not show the reaction selector.
5. Duplicate category by the same user is rejected.
6. Removing a reaction requires that the exact category was previously set by that user on the current reaction target.

## Scenario 9. Deleting a proposal
1. Proposal author presses Delete.
2. Backend verifies ownership.
3. Backend verifies proposal is not in the past.
4. Proposal is deleted.
5. Remaining group state is recalculated naturally by the next Home read.

## Scenario 10. Browsing the catalog
1. User opens Card Catalog.
2. Current proposal is shown in the center.
3. Left/right preview cards are shown when available.
4. Clicking preview card changes `catalog_index` in session state.
5. The page reruns without losing login state.

---

# 19. Security model

## 19.1 Authentication
- all private routes require JWT
- logout is implemented using token revocation, not just client-side deletion

## 19.2 Password storage
- passwords are hashed with Argon2id
- no plaintext password is stored

## 19.3 Input protection
- Pydantic schemas validate request bodies
- service layer rechecks business rules
- category normalization rejects invalid reaction values

## 19.4 Known security tooling
The repository is wired for:
- `bandit`
- `flake8`
- `pytest`
- `radon`
- `locust`

These correspond directly to the project quality requirements and PM plan. fileciteturn5file0 fileciteturn5file1

---

# 20. CI / local quality automation

## Files
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

## Local pre-commit checks
- flake8 on `src/`
- bandit on `src/`

## CI checks
- poetry install
- flake8
- bandit
- radon cc
- radon mi
- pytest with coverage threshold

## Current practical note
The CI structure exists, but the test suite in the archive is still mostly placeholder-based. Therefore the architecture is ready for quality enforcement, while the actual coverage depth still needs to catch up.

---

# 21. Time handling

## Files
- `src/movienight/core/clock.py`
- `src/movienight/services/*`

The project normalizes time comparisons via UTC helpers.

This is important because:
- proposals are compared against “now” often
- votes lock based on time windows
- reactions also depend on the start time window and on whether the proposal is the current reaction target
- winner visibility depends on the lock window

A central helper (`as_utc`) avoids mixing timezone-aware and naive datetimes in comparisons.

---

# 22. Design choices and rationale

## Why group conflicts dynamically
Because schedule conflicts are naturally graph-like and easier to derive from overlaps than to persist as static groups.

## Why expose UI flags from backend
Because voting and reaction availability are business rules. The backend should remain the source of truth.

## Why keep the frontend simple
The assignment prioritizes correctness, quality gates, and demonstrable logic over heavy frontend engineering.

## Why include a schedule endpoint
Even though the main app flow is already covered by Home and Catalog, weekly schedule data helps manual verification and future UI growth.

---

# 23. Non-goals / current gaps

## 23.1 Real external movie integration
`src/movienight/integrations/movie_provider.py` is currently a stub adapter.

The shape is prepared for future integration, but there is no real external movie search provider wired into the user flow yet.

## 23.2 Real test depth
`tests/` currently contains placeholder tests rather than full reliability coverage.

## 23.3 Full route-locking on the Streamlit side
The backend is protected properly, but the frontend still uses a lightweight page-guard approach rather than a single global router that blocks every non-login page before rendering.

---

# 24. Summary

Movie Night is a layered FastAPI + SQLite + Streamlit application whose core value lies in schedule conflict handling and deterministic voting logic.

The most important implemented mechanics are:
- secure authentication
- proposal creation with timing validation
- overlap-based conflict groups
- one-vote-per-group behavior
- deterministic winner selection
- time-gated snack reactions
- grouped home read model for frontend simplicity
- card-based catalog browsing

The project is already structured in a way that is friendly to:
- automated quality gates
- incremental testing expansion
- future integration work
- clear separation of concerns between UI, API, business logic, and persistence