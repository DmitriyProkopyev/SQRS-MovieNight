# Запись демонстрации задачи 5.4

Извлечение SQLCipher-ключа из Conjur Open Source через CLI-команду.

## Перед записью

Поднять стек и убедиться, что переменная не пустая:

```bash
docker compose -f docker-compose.conjur.yaml up -d
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable get -i sqlite-policy/sqlite/key
```

Должно вернуться 64 hex-символа. Любой другой ответ — пройти «Cold start» ниже.

## В кадре

```bash
# 1. политика: кто может читать переменную
cat infra/conjur/conf/policy/sqlite-proxy.yml

# 2. стек поднят
docker compose -f docker-compose.conjur.yaml ps

# 3. извлечение ключа (ключевой кадр)
./scripts/demo_get_key.sh

# 4. без auth → HTTP 401 (опционально, ~10 сек)
curl -sk https://localhost:8443/secrets/myConjurAccount/variable/sqlite-policy%2Fsqlite%2Fkey \
  -o /dev/null -w "HTTP %{http_code}\n"
```

## Cold start

Нужен при первом подъёме на машине или после рестарта Conjur-контейнера (Postgres под Conjur без volume — состояние теряется). Bootstrap печатает admin API-key, поэтому делать **до** записи.

```bash
# 1) .env с мастер-ключом Conjur
[ -f .env ] || cat > .env <<EOF
CONJUR_DATA_KEY=$(docker run --rm cyberark/conjur data-key generate)
EOF
chmod 600 .env

# 2) поднять стек (Conjur стартует ~20-30 сек)
docker compose -f docker-compose.conjur.yaml up -d

# 3) bootstrap: аккаунт + политика + API-key хоста
chmod u+w src/proxy/conjur_token 2>/dev/null || true
./infra/conjur/bootstrap.sh

# 4) положить демо-значение в переменную
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable set -i sqlite-policy/sqlite/key -v "$(openssl rand -hex 32)"

# 5) проверить
./scripts/demo_get_key.sh
```
