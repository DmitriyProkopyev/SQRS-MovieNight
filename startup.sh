#!/usr/bin/env bash
set -euo pipefail

docker network create app_internal >/dev/null 2>&1 || true
docker compose -f docker-compose.conjur.yaml \
               --env-file .env.example \
               run --no-deps --rm conjur data-key generate > data_key
export CONJUR_DATA_KEY="$(< data_key)"

docker compose -f docker-compose.conjur.yaml \
               --env-file .env.example \
               up -d
sleep 10
bash ./infra/conjur/bootstrap.sh
sleep 5

docker compose -f docker-compose.yaml \
               --env-file .env.example \
               up --build -d
docker compose -f docker-compose.yaml --env-file .env.example exec vault \
  vault secrets enable transit
echo "Startup finished."
