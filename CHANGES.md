# CHANGES

## Overview

This change set introduces a protected database access path for the Movie Night project.
The main application no longer needs direct SQLite access at runtime and should communicate with a dedicated SQLite proxy service.
The proxy is responsible for:

- retrieving the SQLCipher encryption key from Conjur Open Source
- opening the encrypted SQLite database
- initializing schema and default data
- exposing internal HTTP endpoints for database-backed business operations

In addition, the infrastructure was extended with:

- HashiCorp Vault in development mode for secret generation/bootstrap
- Conjur Open Source quickstart stack for secret storage and retrieval
- private Docker networking between the application and the proxy

---

## Functional changes

### 1. SQLite Proxy introduced
A new FastAPI-based proxy service was added under `src/proxy/`.
It owns all direct encrypted SQLite access.

Expected responsibilities:

- initialize encrypted DB schema on startup
- retrieve the SQLCipher key from Conjur
- connect to SQLCipher using that key
- provide internal endpoints for DB-backed operations

Examples of internal endpoints:

- `/internal/auth/*`
- `/internal/proposals/*`
- `/internal/votes/*`
- `/internal/reactions/*`
- `/internal/reads/*`

### 2. Main application decoupled from direct SQLite access
The main FastAPI application should call the proxy over HTTP instead of opening SQLite directly.

A proxy client adapter is expected in `src/movienight/integrations/sqlite_proxy_client.py`.

### 3. Encrypted DB access moved to the proxy
The DB/session/model/repository logic should be hosted in the proxy layer.
The SQLCipher connection is built through `src/proxy/connection_provider.py`.

### 4. Container networking hardened
The intended runtime layout is:

- `app` is exposed publicly
- `sqlite-proxy` is **not** exposed publicly
- `app` and `sqlite-proxy` communicate only through a private internal Docker network

### 5. Conjur quickstart integration added
Conjur Open Source is used as the source of truth for the SQLite encryption key.
The proxy authenticates as a Conjur host identity and fetches the variable:

- `sqlite-policy/sqlite/key`

---

## Important files changed or added

### Infrastructure
- `docker-compose.yaml`
- `docker-compose.conjur.yaml`
- `Dockerfile`
- `.env.example`
- `vault/policies/sqlite-key-policy.hcl`
- `infra/conjur/conf/default.conf`
- `infra/conjur/conf/tls/tls.conf`
- `infra/conjur/conf/policy/sqlite-proxy.yml`

### Proxy service
- `src/proxy/main.py`
- `src/proxy/api/router.py`
- `src/proxy/api/deps.py`
- `src/proxy/api/internal_auth.py`
- `src/proxy/api/internal_proposals.py`
- `src/proxy/api/internal_votes.py`
- `src/proxy/api/internal_reactions.py`
- `src/proxy/api/internal_reads.py`
- `src/proxy/api/models.py`
- `src/proxy/db/session.py`
- `src/proxy/db/init_db.py`
- `src/proxy/db/init_schema.py`
- `src/proxy/connection_provider.py`
- copied/ported DB layer under `src/proxy/db/`
- copied/ported repositories under `src/proxy/repositories/`
- copied/ported DB-facing services under `src/proxy/services/`

### Main application
- `src/movienight/main.py`
- `src/movienight/api/db_deps.py`
- `src/movienight/api/deps.py`
- `src/movienight/api/auth_repositories.py`
- `src/movienight/api/auth_required_user.py`
- `src/movienight/integrations/sqlite_proxy_client.py`
- `src/movienight/integrations/sqlite_proxy_repositories.py`
- DB-facing service adapters in `src/movienight/services/`

### Dependency management
- `pyproject.toml`
- `poetry.lock`

---

## Containerized run pipeline

The pipeline below assumes that:

- Docker is installed
- the Conjur quickstart config files exist
- Vault config and policies exist
- dependencies in the application image are already declared in `pyproject.toml`

### Step 1. Start the Conjur quickstart stack

```bash
mkdir -p infra/conjur/conf/tls infra/conjur/conf/policy data

docker compose -f docker-compose.conjur.yaml down -v

docker compose -f docker-compose.conjur.yaml run --no-deps --rm conjur data-key generate > data_key
export CONJUR_DATA_KEY="$(< data_key)"

docker compose -f docker-compose.conjur.yaml run --no-deps --rm openssl

docker compose -f docker-compose.conjur.yaml up -d
```

### Step 2. Initialize Conjur account and client

```bash
docker compose -f docker-compose.conjur.yaml exec conjur conjurctl account create myConjurAccount > admin_data

docker compose -f docker-compose.conjur.yaml exec client conjur init oss -u https://proxy -a myConjurAccount --self-signed
```

### Step 3. Login to Conjur as admin

```bash
docker compose -f docker-compose.conjur.yaml exec client conjur login -i admin
```

Use the admin API key from `admin_data` when prompted.

### Step 4. Load the policy for the SQLite proxy host and variable

```bash
docker compose -f docker-compose.conjur.yaml exec client conjur policy load -b root -f /policy/sqlite-proxy.yml
```

### Step 5. Obtain or rotate the API key for the proxy host

If the host was created under `sqlite-policy`, use the fully qualified id:

```bash
docker compose -f docker-compose.conjur.yaml exec client conjur host rotate-api-key -i sqlite-policy/database-proxy
```

Store the returned API key in:

```bash
printf '%s' '<HOST_API_KEY>' > src/proxy/conjur_token
chmod 600 src/proxy/conjur_token
```

### Step 6. Put the SQLite encryption key into Conjur

```bash
SQLITE_KEY=$(openssl rand -hex 32 | tr -d '\r\n')
docker compose -f docker-compose.conjur.yaml exec client conjur variable set -i sqlite-policy/sqlite/key -v "$SQLITE_KEY"
```

### Step 7. Start Vault

```bash
docker compose -f docker-compose.yaml up -d vault
```

### Step 8. Build and start the application stack

```bash
docker compose -f docker-compose.yaml up --build -d
```

This stack should contain at minimum:

- `vault`
- `app`
- `sqlite-proxy`

---

## Local manual run pipeline (hybrid mode)

This mode is useful for debugging on the host while Conjur and Vault run in Docker.

### Step 1. Start the proxy locally

```bash
uvicorn --app-dir src proxy.main:app --host 0.0.0.0 --port 9000
```

### Step 2. Start the main app locally in another terminal

```bash
uvicorn --app-dir src movienight.main:app --host 0.0.0.0 --port 8000
```

---

## Basic test plan

### Health checks

```bash
curl http://127.0.0.1:9000/health
curl http://127.0.0.1:8000/health
curl -k https://localhost:8443
```

Expected:

- proxy returns `{"status":"ok"}`
- main app returns `{"status":"ok"}`
- Conjur proxy responds over HTTPS

### Conjur variable sanity check

Inside the Conjur client container:

```bash
docker compose -f docker-compose.conjur.yaml exec client conjur variable value -i sqlite-policy/sqlite/key
```

Expected:

- the variable exists and returns a non-empty value

### API smoke test

1. Register a user through the main API
2. Login and obtain JWT
3. Create a proposal
4. Vote for a proposal
5. Add/remove a snack reaction
6. Open `/docs` on both main app and proxy and verify endpoints are present

### Proxy isolation check

The proxy should not have a published port in the fully containerized deployment.
Only the main app should be reachable from outside the internal Docker network.

---

## Notes

- If `conjur init oss -u https://proxy ...` fails with `connection refused`, the nginx proxy configuration or TLS mounts are wrong.
- If the proxy fails with `401 Unauthorized`, the host API key in `src/proxy/conjur_token` is stale or incorrect.
- If the proxy fails with SQLCipher startup errors, delete the local DB file and recreate it:

---