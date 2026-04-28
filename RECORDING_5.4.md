# Запись демонстрации задачи 5.4

Извлечение SQLCipher-ключа из Conjur Open Source через CLI-команду. Все действия — от лица sqlite-proxy: он же синхронизирует ключ из Vault в Conjur (Transit engine), он же потом читает его обратно по своей host identity (`host/sqlite-policy/database-proxy`).

Видео без звука — все команды читаются с экрана.

## Перед записью

Поднять оба стека и убедиться, что чтение и sync проходят:

```bash
docker compose -f docker-compose.conjur.yaml up -d
docker compose -f docker-compose.yaml up -d

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"
```

Любая ошибка — пройти «Cold start» ниже.

## В кадре

```bash
# 1. политика: что разрешено хосту прокси
cat infra/conjur/conf/policy/sqlite-proxy.yml

# 2. оба стека подняты
docker compose -f docker-compose.conjur.yaml ps
docker compose -f docker-compose.yaml ps

# 3. прокси ЧИТАЕТ текущий ключ из Conjur (host identity, runtime path)
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"

# 4. прокси СИНХРОНИЗИРУЕТ новый ключ: vault transit/random/32 -> conjur variable set
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"

# 5. прокси ЧИТАЕТ снова — значение другое, его положил сам прокси
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"
```

Опционально — внешняя проверка от admin'а через Conjur CLI в `client`-контейнере (видно, что то же значение):

```bash
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable get -i sqlite-policy/sqlite/key
```

Все шаги (3–5) выполняют код из `src/proxy/connection_provider.py`:
- `ConjurClient` — читает токен из `src/proxy/conjur_token`, ходит в Conjur по HTTPS,
- `init_encryption_key` — Vault Transit `random_bytes(32)` → `ConjurClient().set_encryption_key(...)`.

## Cold start

Нужен при первом подъёме на машине или после рестарта Conjur/Vault-контейнера (Postgres под Conjur и Vault dev-mode оба без volume — состояние теряется). Bootstrap печатает admin API-key Conjur, поэтому делать **до** записи.

```bash
# 1) .env с мастер-ключом Conjur (создаётся один раз)
[ -f .env ] || cat > .env <<EOF
CONJUR_DATA_KEY=$(docker run --rm cyberark/conjur data-key generate)
SQLITE_PROXY_URL=http://sqlite-proxy:9000
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=root
EOF
chmod 600 .env

# 2) Conjur stack: поднять, дождаться готовности (~30 сек),
#    выполнить bootstrap (аккаунт, политика, ротация API-key хоста)
docker compose -f docker-compose.conjur.yaml up -d
chmod u+w src/proxy/conjur_token 2>/dev/null || true
./infra/conjur/bootstrap.sh

# 3) App stack: поднять Vault и sqlite-proxy
docker compose -f docker-compose.yaml up -d

# 4) Включить Transit engine на Vault (dev-mode стартует без него)
docker exec -e VAULT_TOKEN=root -e VAULT_ADDR=http://127.0.0.1:8200 \
  movienight-vault vault secrets enable transit

# 5) Прогнать sync, чтобы переменная имела значение к началу записи
docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import init_encryption_key; init_encryption_key(); print('OK')"

docker compose -f docker-compose.yaml exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())"
```
