# Recording task 5.4

Extracting the SQLCipher key from Conjur Open Source via a CLI command. All actions are performed by sqlite-proxy: it both syncs the key from Vault into Conjur (via the Transit engine) and reads it back using its host identity (`host/sqlite-policy/database-proxy`).

## Before recording

Bring up both stacks and confirm read and sync both work:

```bash
docker compose -f docker-compose.conjur.yaml up -d
docker compose -f docker-compose.yaml up -d

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"
```

If anything fails — go through "Cold start" below.

## On camera

```bash
# 1. policy: what the proxy host is allowed to do
cat infra/conjur/conf/policy/sqlite-proxy.yml

# 2. both stacks are up
docker compose -f docker-compose.conjur.yaml ps
docker compose -f docker-compose.yaml ps

# 3. proxy READS the current key from Conjur (host identity, runtime path)
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"

# 4. proxy SYNCS a new key: vault transit/random/32 -> conjur variable set
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"

# 5. proxy READS again — the value is different, the proxy itself put it there
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"
```

Optional — external sanity check from admin via the Conjur CLI in the `client` container (shows the same value):

```bash
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable get -i sqlite-policy/sqlite/key
```

Steps 3–5 all execute code from `src/proxy/connection_provider.py`:
- `ConjurClient` — reads the token from `src/proxy/conjur_token`, talks to Conjur over HTTPS,
- `init_encryption_key` — Vault Transit `random_bytes(32)` → `ConjurClient().set_encryption_key(...)`.

## Cold start

Required on the first time the stack is brought up on a machine, and after any restart of the Conjur or Vault container (Postgres under Conjur and Vault dev-mode are both volumeless — state is lost). `bootstrap.sh` prints the Conjur admin API key, so run it **before** recording.

```bash
# 1) .env with the Conjur master key (created once)
[ -f .env ] || cat > .env <<EOF
CONJUR_DATA_KEY=$(docker run --rm cyberark/conjur data-key generate)
SQLITE_PROXY_URL=http://sqlite-proxy:9000
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=root
EOF
chmod 600 .env

# 2) Conjur stack: bring up, wait for readiness (~30 s),
#    run bootstrap (account, policy, host API-key rotation)
docker compose -f docker-compose.conjur.yaml up -d
chmod u+w src/proxy/conjur_token 2>/dev/null || true
./infra/conjur/bootstrap.sh

# 3) App stack: bring up Vault and sqlite-proxy
docker compose -f docker-compose.yaml up -d

# 4) Enable the Transit engine on Vault (dev-mode starts without it)
docker exec -e VAULT_TOKEN=root -e VAULT_ADDR=http://127.0.0.1:8200 \
  movienight-vault vault secrets enable transit

# 5) Run sync once so the variable holds a value before recording starts
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"
```
