# Recording task 5.6

The SQLCipher key lives only inside `sqlite-proxy`. The main application talks to the proxy over HTTP and never touches the key directly. Task 5.6 demonstrates this empirically: a memory snapshot of the main app's process must not contain the key, and the same snapshot taken from the proxy must contain it (positive control).

## Before recording

The full stack must be up and healthy — see `RECORDING_5.4.md` ("Cold start") for how to get there.

On top of that, the main application must have actually exercised its database path through the proxy at least once. Otherwise the demonstration is hollow: a process that never used the database would trivially not contain the key. The simplest way is to hit a DB-using endpoint a few times (e.g. register a couple of users via `/api/v1/auth/register`). After that, both processes will have done real work and the proxy will have fetched, used, and held the key in memory at least once.

`gcore` is required, and it needs `sudo` because the container processes run as root on the host. Confirm passwordless `sudo` is configured, or be ready to type the password on camera.

## On camera

```bash
# 1. Pull the current key from Conjur via the proxy's runtime path
KEY=$(docker compose exec -T -e PYTHONPATH=/app/src sqlite-proxy \
  python -c "from proxy.connection_provider import ConjurClient; print(ConjurClient().get_encryption_key())" \
  | tr -d '\r\n')
echo "key=$KEY (len=${#KEY})"

# 2. Resolve container PIDs to host PIDs
APP_PID=$(docker inspect -f '{{.State.Pid}}' sqrs-movienight-app-1)
PROXY_PID=$(docker inspect -f '{{.State.Pid}}' sqrs-movienight-sqlite-proxy-1)
echo "app=$APP_PID  proxy=$PROXY_PID"

# 3. Snapshot both processes (~340 MB each)
mkdir -p /tmp/dumps
sudo gcore -o /tmp/dumps/app   "$APP_PID"
sudo gcore -o /tmp/dumps/proxy "$PROXY_PID"

# 4. Main result: key absent from main app memory
sudo grep -ao "$KEY" /tmp/dumps/app.$APP_PID   | wc -l   # expect 0

# 5. Positive control: key present in proxy memory (proves the method works)
sudo grep -ao "$KEY" /tmp/dumps/proxy.$PROXY_PID | wc -l # expect > 0

# 6. Clean up the dumps
sudo rm /tmp/dumps/app.$APP_PID /tmp/dumps/proxy.$PROXY_PID
```

Step 5 is what makes step 4 meaningful. Without the positive control, "no matches" could just mean the search method is broken; with it, the zero count on the main app is real evidence that the SQLCipher key is not present in the main app's address space.
