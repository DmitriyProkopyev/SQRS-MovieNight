# Запись демонстрации задачи 5.4

Извлечение SQLCipher-ключа из Conjur Open Source через CLI-команду. Ключ перед извлечением кладётся в Conjur самим прокси, который генерирует его в HashiCorp Vault через Transit engine.

## Перед записью

Поднять оба стека и убедиться, что sync проходит:

```bash
docker compose -f docker-compose.conjur.yaml up -d
docker compose -f docker-compose.yaml up -d
./scripts/demo_sync_key_from_vault.sh   # должно вернуть 'OK'
./scripts/demo_get_key.sh               # должно вернуть 64 hex-символа
```

Любая ошибка — пройти «Cold start» ниже.

## В кадре

```bash
# 1. политика: кому разрешено читать и писать переменную
cat infra/conjur/conf/policy/sqlite-proxy.yml

# 2. оба стека подняты
docker compose -f docker-compose.conjur.yaml ps
docker compose -f docker-compose.yaml ps

# 3. значение в Conjur ДО sync
./scripts/demo_get_key.sh

# 4. прокси: vault transit/random/32 -> conjur variable set (ключевой кадр)
./scripts/demo_sync_key_from_vault.sh

# 5. значение в Conjur ПОСЛЕ sync — другое, его положил прокси
./scripts/demo_get_key.sh
```

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
./scripts/demo_sync_key_from_vault.sh
./scripts/demo_get_key.sh
```
