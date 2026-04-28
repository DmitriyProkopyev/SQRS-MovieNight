# Запись демонстрации задачи 5.4

> Извлечение ключа шифрования SQLite из Conjur Open Source через CLI-команду.

Цель видео — показать, что команда из CLI возвращает значение, лежащее в Conjur, и из кадра очевидно, что:
- ключ хранится в централизованном секрет-брокере, а не в коде/конфиге репозитория,
- его читает только авторизованный субъект (политика загружена и работает),
- сам канал доступа защищён (HTTPS).

Всё, что описано ниже, проверено на текущем состоянии репозитория `feature/conjur-policy-and-key-demo` (HEAD `f68778c`) — команды выполнены, выводы зафиксированы.

---

## Что попадает в кадр

Минимально (≈ 30 секунд) — три команды:

1. содержимое политики `infra/conjur/conf/policy/sqlite-proxy.yml`,
2. `docker compose -f docker-compose.conjur.yaml ps` — стек поднят,
3. `./scripts/demo_get_key.sh` — извлекаем ключ.

Рекомендуемое расширение (≈ 60 секунд) — добавить четвёртый кадр с проверкой enforcement (см. кадр 4 ниже). Это ровно то, что отличает «прокачанную» демонстрацию от формальной: показывает не только happy path, но и что без авторизации Conjur ничего не отдаёт.

---

## Pre-flight (выполнить ДО записи)

Все проверки делать в свежем терминале, в каталоге репозитория:

```bash
cd /home/devasc/inno/SQRS-MovieNight
```

### 1. Стек Conjur поднят (4 сервиса в `Up`)

```bash
docker compose -f docker-compose.conjur.yaml ps
```

Должно быть видно ровно эти контейнеры в статусе `Up`:
- `movienight-conjur-conjur-1` — Conjur server (Ruby/Rails)
- `movienight-conjur-database-1` — Postgres под Conjur
- `movienight-conjur-proxy-1` — nginx, терминатор TLS перед Conjur
- `movienight-conjur-client-1` — контейнер с Conjur CLI v9, через который мы и шлём команду

Если хотя бы одного нет или статус `Restarting` — иди в раздел «Подготовка с нуля».

### 2. Переменная имеет значение

```bash
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable get -i sqlite-policy/sqlite/key
```

Должна вернуться строка из 64 hex-символов, например:
```
7abdaa5284ecbe7617fd2d409df728abfac18cb0a5f5ef97f334911b811cbe08
```

Если вернулось `Variable empty` — переменная объявлена, но пустая. Заполни:

```bash
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable set -i sqlite-policy/sqlite/key -v "$(openssl rand -hex 32)"
```

Если вернулось `Authentication required` — у клиента истекла сессия. Просто перезайди:

```bash
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur login --id admin \
  --password "$(docker compose -f docker-compose.conjur.yaml exec -T conjur \
                   conjurctl role retrieve-key myConjurAccount:user:admin | tr -d '\r\n')"
```

### 3. Демонстрационный скрипт исполнимый

```bash
ls -l scripts/demo_get_key.sh
# rwx должен быть у владельца
./scripts/demo_get_key.sh
```

---

## Подготовка с нуля (если pre-flight не прошёл)

Эта последовательность приводит систему в состояние, годное для записи. Postgres под Conjur не имеет персистентного volume — после рестарта контейнера состояние теряется и нужен полный re-bootstrap.

```bash
# 1) .env должен содержать CONJUR_DATA_KEY (мастер-ключ Conjur).
#    Если файла нет — сгенерировать и сохранить (один раз):
[ -f .env ] || cat > .env <<EOF
CONJUR_DATA_KEY=$(docker run --rm cyberark/conjur data-key generate)
SQLITE_PROXY_URL=http://sqlite-proxy:9000
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=root
EOF
chmod 600 .env

# 2) Поднять стек
docker compose -f docker-compose.conjur.yaml up -d

# 3) Дождаться готовности Conjur (логи перестают спамить миграциями ~20-30 сек).
#    Признак готовности — в логах появляется приём HTTP-запросов на /health.
docker compose -f docker-compose.conjur.yaml logs --tail=5 conjur

# 4) Bootstrap: создаёт аккаунт myConjurAccount, грузит политику,
#    ротирует API-key хоста database-proxy в src/proxy/conjur_token
chmod u+w src/proxy/conjur_token 2>/dev/null || true
./infra/conjur/bootstrap.sh

# 5) Положить демо-значение в переменную
docker compose -f docker-compose.conjur.yaml exec -T client \
  conjur variable set -i sqlite-policy/sqlite/key -v "$(openssl rand -hex 32)"

# 6) Перепроверить pre-flight
./scripts/demo_get_key.sh
```

Bootstrap печатает в stdout admin API-key. **Если делал bootstrap при включённой записи — пересними.**

---

## Сценарий записи

Состояние терминала перед началом:
- свежая сессия (история не нужна) или `clear` (Ctrl-L) перед каждым кадром,
- Do Not Disturb включён, мессенджеры/почта закрыты,
- IDE с открытыми файлами `src/proxy/conjur_token`, `.env` свёрнуто/закрыто,
- размер шрифта в терминале — крупный, видно из-за плеча.

### Кадр 1 — политика (≈ 15 сек)

Реплика:
> «В Conjur объявлена переменная `sqlite-policy/sqlite/key`. По политике её может прочитать только один хост — sqlite-proxy. Все остальные роли отбиваются по deny-by-default.»

Команда:
```bash
cat infra/conjur/conf/policy/sqlite-proxy.yml
```

В выводе курсором выделить три блока:
- `!host id: database-proxy` — машинная identity прокси,
- `!variable id: sqlite/key` — сама переменная,
- `!permit role: !host database-proxy ... resource: !variable sqlite/key` с `privileges: [read, execute]` — единственное разрешение.

Шапка файла (комментарии) объясняет модель ровно теми же словами — её можно тоже задержаться показать, если хочется усилить.

### Кадр 2 — стек поднят (≈ 5 сек)

Реплика:
> «Стек Conjur Open Source запущен локально через docker compose:»

Команда:
```bash
docker compose -f docker-compose.conjur.yaml ps
```

В кадре — четыре контейнера в `Up`. На вопрос «что есть что», коротко:
- `conjur` — сам сервер,
- `database` — Postgres под него,
- `proxy` — nginx перед Conjur, терминирует HTTPS на порту 8443,
- `client` — CLI-контейнер, через который ходим.

### Кадр 3 — извлечение ключа (≈ 10 сек) — **ключевой кадр задачи**

Реплика:
> «Извлекаем ключ из Conjur одной командой через CLI. Скрипт — это обёртка над `conjur variable get`, без сюрпризов:»

Команда:
```bash
./scripts/demo_get_key.sh
```

Ожидаемый вывод (одна строка с командой и одна со значением):
```
==> conjur variable get -i sqlite-policy/sqlite/key
7abdaa5284ecbe7617fd2d409df728abfac18cb0a5f5ef97f334911b811cbe08
```

Реплика после вывода:
> «Это 32-байтовый ключ SQLCipher в hex. Прокси использует его в `PRAGMA key`, чтобы открыть зашифрованный файл базы.»

Если хочется, перед запуском можно показать сам скрипт — он короткий (`cat scripts/demo_get_key.sh`), это снимет вопрос «а что внутри обёртки».

### Кадр 4 — enforcement (≈ 10 сек, опционально, но желательно)

Реплика:
> «Проверим, что доступ действительно ограничен. Тот же endpoint Conjur, но без авторизации:»

Команда:
```bash
curl -sk https://localhost:8443/secrets/myConjurAccount/variable/sqlite-policy%2Fsqlite%2Fkey \
  -o /dev/null -w "HTTP %{http_code}\n"
```

Ожидаемый вывод:
```
HTTP 401
```

Реплика:
> «Без действительного токена Conjur не отдаёт ничего — ни админу, ни хосту, ни анонимному запросу. Это не проверка в коде приложения, это сам Conjur.»

---

## Что НЕ должно попасть в кадр

| Объект | Почему | Что вместо этого |
|---|---|---|
| `cat src/proxy/conjur_token` | Реальный API-key хоста sqlite-proxy. Утечка = чтение переменной от его имени | `ls -l src/proxy/conjur_token` если нужно показать факт существования |
| `cat .env` | Содержит `CONJUR_DATA_KEY` (мастер-ключ шифрования базы Conjur) | Не открывать |
| Запуск `bootstrap.sh` на камере | Печатает admin API-key в stdout | Запустить ДО записи |
| История shell (стрелка вверх, `history`) | Может содержать старые токены / ключи / `--password` | Свежий терминал, либо `unset HISTFILE` перед записью |
| Уведомления десктопа | Лишний шум, иногда раскрывают почту/контакты | DND перед записью |
| Открытые вкладки браузера c GitHub Settings → Tokens | Утечка | Закрыть |
| `env | grep -i conjur` | Покажет CONJUR_DATA_KEY и токены | Не делать |

---

## Если на камере что-то пошло не так

| Симптом | Причина | Что сделать |
|---|---|---|
| `Variable empty` | Переменная не заполнена | Стоп, идти в Подготовка → шаг 5, потом пересъёмка |
| `Could not connect to Conjur` | Контейнер `conjur` упал | Стоп, `docker compose -f docker-compose.conjur.yaml up -d`, дождаться готовности |
| `Authentication required` от CLI | Сессия admin'а в client-контейнере истекла | Перезайти (см. pre-flight шаг 2) |
| Скрипт `Permission denied` | Файл без +x | `chmod +x scripts/demo_get_key.sh`. На клонe и в HEAD ветки бит уже выставлен — должно быть редко |
| Conjur в `Restarting` | Скорее всего отсутствует/пустой `CONJUR_DATA_KEY` в `.env` | Подготовка с нуля → шаг 1 |

---

## Технический контекст

Справка по тому, как устроена показанная схема — на случай, если по ходу обсуждения потребуется детализация.

### Источник значения переменной

В демонстрации значение поставлено вручную командой `conjur variable set` (шаг 5 cold-start). В прод-сценарии ключ генерируется в HashiCorp Vault через Transit engine (`vault_client.secrets.transit.generate_random_bytes(n_bytes=32)`) и синхронизируется в Conjur — см. `init_encryption_key` в `src/proxy/connection_provider.py`. Vault — источник правды, Conjur — точка авторизованной выдачи. Разделение даёт separation of duties: компрометация одного из двух не даёт ключ.

### Граница доверия к Conjur

В `SECURITY.md` → «What This Does Not Protect Against», пункт 3, явно зафиксировано: «Compromise of the centralized secret stores: the security of Vault and Conjur themselves is assumed.» Self-hosted self-signed Conjur — это сознательный выбор корня доверия, а не упущение.

### Контроль доступа к переменной

В политике один-единственный `!permit`: роль `!host database-proxy`, привилегии `[read, execute]`, ресурс `!variable sqlite/key`. У Conjur deny-by-default — отсутствие `!permit` означает, что роль не получит ничего. Admin сохраняет суперюзерский доступ по дизайну Conjur, но его API-key хранится out-of-band и ни в один сервис не деплоится.

### Защита API-key хоста sqlite-proxy

Файл `src/proxy/conjur_token` имеет несколько уровней защиты:
- смонтирован read-only внутрь контейнера sqlite-proxy, права `0400` на хосте,
- API-key ротируется командой `conjur host rotate-api-key -i sqlite-policy/database-proxy` — старый инвалидируется немедленно,
- это API-key одного хоста, не root-токен; даже утечка ограничена политикой sqlite-policy,
- доступ к самому файлу подразумевает full host compromise — это явно вне модели угроз (см. `SECURITY.md`).

### Шифрование канала proxy ↔ Conjur

nginx внутри Conjur-стека терминирует TLS на порту 443 (`infra/conjur/conf/default.conf`), self-signed cert лежит в `infra/conjur/conf/tls/nginx.crt`, его SAN включает `DNS:proxy`. SDK на стороне прокси (`conjur-api` Python SDK) валидирует cert в режиме `SslVerificationMode.SELF_SIGN` с явно переданным `cert_file`. `verify=False`-обходов в коде нет.

### Разделение ролей Vault и Conjur

Vault и Conjur — разные задачи. Vault: generation, rotation, PKI, Transit. Conjur: fine-grained RBAC доступа к существующим секретам со стороны множества machine identity. У нас Vault генерирует, Conjur публикует строго одной identity. Это повторяет паттерн, типичный для CyberArk-стека.

### Изоляция ключа от main app

По архитектуре (см. `SECURITY.md` → «Conceptual Approach») главное приложение `movienight` не знает ни про Conjur, ни про токен. Оно ходит только в sqlite-proxy по HTTP; в Conjur за ключом ходит sqlite-proxy. Memory dump главного приложения не возвращает ничего, относящегося к ключу.

---

## Чек-лист перед публикацией видео

- [ ] В кадре нет: содержимого `src/proxy/conjur_token`, `.env`, admin API-key, вывода `bootstrap.sh`.
- [ ] В кадре есть: имя переменной (`sqlite-policy/sqlite/key`), политика с `!permit`, команда извлечения, её вывод.
- [ ] Если включён кадр 4 — виден код `HTTP 401` без auth.
- [ ] Между кадрами нет лишних действий (опечаток, истории команд, переключений в IDE с токенами).
- [ ] Аудио без посторонних шумов / уведомлений.
- [ ] Длительность: ≤ 60 сек если только демо, ≤ 90 сек с enforcement-кадром. Дольше — это уже не 5.4, это лекция.
- [ ] Воспроизведено хотя бы один раз с нуля (через раздел «Подготовка с нуля»), чтобы убедиться: демо не зависит от текущего состояния машины.

---

## Границы задачи 5.4

5.4 покрывает только извлечение ключа из Conjur. В этот видео-кадр сознательно не входят смежные части системы:

- runtime-использование ключа в sqlite-proxy — демонстрируется отдельно при поднятом основном стеке `docker-compose.yaml` (см. коммит `f68778c`),
- синхронизация Vault → Conjur — реализована в `init_encryption_key` (`src/proxy/connection_provider.py`), в кадр не входит,
- ротация хост-ключа (`conjur host rotate-api-key`) — отдельный сценарий.
