#!/usr/bin/env bash
# Demo: retrieve the SQLCipher encryption key from Conjur Open Source via the
# Conjur CLI. This is the simplest end-to-end demonstration that the policy
# is loaded and the variable can be read inside the Conjur stack.
#
# Recording-friendly: prints the variable id and the returned value with
# minimal noise.

set -euo pipefail

COMPOSE_FILE="docker-compose.conjur.yaml"
VARIABLE_ID="sqlite-policy/sqlite/key"

echo "==> conjur variable get -i $VARIABLE_ID"
docker compose -f "$COMPOSE_FILE" exec -T client \
  conjur variable get -i "$VARIABLE_ID"
