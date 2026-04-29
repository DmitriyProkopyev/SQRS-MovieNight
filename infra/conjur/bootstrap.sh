#!/usr/bin/env bash
# Bootstrap the Conjur Open Source stack for SQLite proxy key access.
#
# Prerequisite: the Conjur compose stack is already running:
#   docker compose -f docker-compose.conjur.yaml up -d
#
# This script:
#   1. Creates the Conjur account `myConjurAccount` (idempotent: skipped if it already exists)
#   2. Initializes the CLI inside the `client` container
#   3. Logs in as admin
#   4. Loads `infra/conjur/conf/policy/sqlite-proxy.yml` at branch `root`
#   5. Rotates the API key for host `sqlite-policy/database-proxy`
#   6. Writes that API key to `src/proxy/conjur_token` with mode 0400
#
# After this finishes, the SQLite proxy can authenticate to Conjur and fetch
# the encryption key. To populate the variable itself with a value, see the
# Vault sync workflow (`init_encryption_key()` in `src/proxy/connection_provider.py`)
# or set a demo value manually with `conjur variable set`.

set -euo pipefail

COMPOSE_FILE="docker-compose.conjur.yaml"
ACCOUNT="movienight"
POLICY_FILE_IN_CLIENT="/policy/sqlite-proxy.yml"
HOST_ID="sqlite-policy/database-proxy"
TOKEN_OUTPUT="src/proxy/conjur_token"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "error: $COMPOSE_FILE not found. Run this script from the repository root." >&2
  exit 1
fi

dc() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

echo "==> verifying Conjur stack is running"
if ! dc ps --status running --services | grep -qx conjur; then
  echo "error: conjur service is not running. Start the stack first:" >&2
  echo "       docker compose -f $COMPOSE_FILE up -d" >&2
  exit 1
fi

echo "==> creating account '$ACCOUNT' (idempotent)"
account_create_output="$(dc exec -T conjur conjurctl account create "$ACCOUNT" 2>&1 || true)"

if echo "$account_create_output" | grep -q "already exists"; then
  echo "    account already exists; admin API key not re-emitted by Conjur."
  echo "    if you do not have it saved, recover with:"
  echo "      docker compose -f $COMPOSE_FILE exec conjur conjurctl role retrieve-key $ACCOUNT:user:admin"
  ADMIN_API_KEY="$(dc exec -T conjur conjurctl role retrieve-key "$ACCOUNT:user:admin" | tr -d '\r\n')"
else
  echo "$account_create_output"
  ADMIN_API_KEY="$(echo "$account_create_output" \
    | awk -F': ' '/API key for admin/ { print $2 }' \
    | tr -d '\r\n')"
fi

if [[ -z "${ADMIN_API_KEY:-}" ]]; then
  echo "error: could not determine admin API key" >&2
  exit 1
fi

echo "==> initializing CLI in client container"
printf "3\n" | dc exec -T client conjur init \
  --url https://proxy \
  --account "$ACCOUNT" \
  --self-signed \
  --force

echo "==> logging in as admin"
dc exec -T client conjur login --id admin --password "$ADMIN_API_KEY"

echo "==> loading policy from $POLICY_FILE_IN_CLIENT"
dc exec -T client conjur policy load --branch root --file "$POLICY_FILE_IN_CLIENT"

echo "==> rotating API key for host $HOST_ID"
HOST_API_KEY="$(dc exec -T client conjur host rotate-api-key -i "$HOST_ID" | tr -d '\r\n')"

if [[ -z "$HOST_API_KEY" ]]; then
  echo "error: rotation produced an empty API key" >&2
  exit 1
fi

echo "==> writing host API key to $TOKEN_OUTPUT (mode 0400)"
mkdir -p "$(dirname "$TOKEN_OUTPUT")"
printf '%s' "$HOST_API_KEY" > "$TOKEN_OUTPUT"
chmod 0600 "$TOKEN_OUTPUT" 2>/dev/null || true

echo
echo "Conjur is bootstrapped."
echo "  account:           $ACCOUNT"
echo "  policy loaded:     $POLICY_FILE_IN_CLIENT"
echo "  proxy host id:     $HOST_ID"
echo "  proxy token file:  $TOKEN_OUTPUT"
echo
echo "Next steps:"
echo "  - populate the variable from Vault (see src/proxy/connection_provider.py:init_encryption_key)"
echo "    or set a demo value:"
echo "      docker compose -f $COMPOSE_FILE exec client \\"
echo "        conjur variable set -i sqlite-policy/sqlite/key -v \"\$(openssl rand -hex 32)\""
echo "  - verify retrieval with: scripts/demo_get_key.sh"
