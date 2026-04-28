#!/usr/bin/env bash
# Demo: trigger the sqlite-proxy to generate a fresh 32-byte key in
# HashiCorp Vault (via Transit) and store it into Conjur under
# sqlite-policy/sqlite/key. After this runs, the value the proxy reads
# from Conjur at runtime is the one Vault just produced.
#
# Recording-friendly: minimal output, exits non-zero on failure.

set -euo pipefail

APP_COMPOSE="docker-compose.yaml"

echo "==> proxy: vault transit/random/32 -> conjur variable set"
docker compose -f "$APP_COMPOSE" exec -T sqlite-proxy python -c "
import sys
sys.path.insert(0, '/app/src')
from proxy.connection_provider import init_encryption_key
init_encryption_key()
print('OK')
"
