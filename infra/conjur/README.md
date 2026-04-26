# Conjur Open Source — Movie Night SQLite key

Conjur Open Source holds the SQLCipher encryption key for the proxy-managed
encrypted SQLite database. Only one machine identity is authorized to read
that key: the SQLite proxy service.

## Files

| Path                                   | Role                                                                    |
|----------------------------------------|-------------------------------------------------------------------------|
| `conf/policy/sqlite-proxy.yml`         | Conjur policy creating the `sqlite-policy/` namespace, the host `sqlite-policy/database-proxy`, the variable `sqlite-policy/sqlite/key`, and the `read,execute` permit. |
| `conf/default.conf`                    | nginx config for the TLS-terminating proxy in front of Conjur.          |
| `conf/tls/tls.conf`                    | OpenSSL config used by the `openssl` service to mint a self-signed cert.|
| `bootstrap.sh`                         | One-shot bootstrap: create account, load policy, rotate proxy API key, write `src/proxy/conjur_token`. |

## First-time bootstrap

```bash
docker compose -f docker-compose.conjur.yaml up -d
./infra/conjur/bootstrap.sh
```

After bootstrap, `src/proxy/conjur_token` contains the API key the proxy
uses to authenticate. The variable is created but empty; populate it via
the Vault sync (`src/proxy/connection_provider.py:init_encryption_key`)
or, for a demo, set it directly:

> **Do not commit `src/proxy/conjur_token` after bootstrap.** It is currently
> tracked with a placeholder (`PUT UR TOKEN HERE`) so the compose bind-mount
> resolves on a clean clone, but after running `bootstrap.sh` it holds a real
> API key. Either revert the file before pushing (`git checkout -- src/proxy/conjur_token`)
> or add a `.gitignore` rule and switch the placeholder to a `.example` file.

```bash
docker compose -f docker-compose.conjur.yaml exec client \
  conjur variable set -i sqlite-policy/sqlite/key -v "$(openssl rand -hex 32)"
```

## Verify retrieval

CLI (uses the `client` container's admin login):

```bash
./scripts/demo_get_key.sh
```

Python SDK (uses the proxy's API token from `src/proxy/conjur_token`,
i.e. the same path the proxy itself takes):

```bash
poetry run python scripts/demo_get_key.py
```

Both should print the 32-byte hex key.

## Authorization model

Conjur enforces deny-by-default. The only `!permit` granting access to
`sqlite-policy/sqlite/key` is the one in `conf/policy/sqlite-proxy.yml`,
and it names a single role: `host sqlite-policy/database-proxy`. No other
application role can read or fetch the variable. The `admin` user retains
super-user access by Conjur design — its API key is expected to remain
out-of-band (operator-only, not deployed to any service).

## Rotating the proxy's API key

```bash
docker compose -f docker-compose.conjur.yaml exec client \
  conjur host rotate-api-key -i sqlite-policy/database-proxy \
  > src/proxy/conjur_token
chmod 0400 src/proxy/conjur_token
```

## Recovering the admin API key

If the bootstrap output was lost:

```bash
docker compose -f docker-compose.conjur.yaml exec conjur \
  conjurctl role retrieve-key myConjurAccount:user:admin
```
