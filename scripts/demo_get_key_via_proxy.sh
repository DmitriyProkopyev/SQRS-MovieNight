#!/usr/bin/env bash
# Demo: have the sqlite-proxy fetch the SQLCipher encryption key from
# Conjur using its own host identity (host/sqlite-policy/database-proxy)
# and the API key in src/proxy/conjur_token. This is the exact runtime
# path the proxy takes on every DB connection in connection_provider.py.
#
# Recording-friendly: prints the variable id and the returned value with
# minimal noise.

set -euo pipefail

APP_COMPOSE="docker-compose.yaml"
VARIABLE_ID="sqlite-policy/sqlite/key"

echo "==> proxy (host/sqlite-policy/database-proxy): get $VARIABLE_ID via host API key"
docker compose -f "$APP_COMPOSE" exec -T sqlite-proxy python -c "
import sys
sys.path.insert(0, '/app/src')
from proxy.connection_provider import ConjurClient
print(ConjurClient().get_encryption_key())
"
