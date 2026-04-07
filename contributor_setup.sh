#!/bin/bash

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "Running pre-commit checks..."

if ! poetry --version >/dev/null 2>&1; then
  echo "[ERROR]: Poetry is not available!"
fi

MAX_RETRIES=3
RETRY_INTERVAL=2
SUCCESS=0

echo "Ensuring dependencies..."

for i in $(seq 1 $MAX_RETRIES); do
  echo "Attempt $i/$MAX_RETRIES: running 'poetry install --no-interaction --no-root'..."
  if poetry install --no-interaction --no-root; then
    SUCCESS=1
    break
  else
    echo "Attempt $i/$MAX_RETRIES failed."
    if [ $i -lt $MAX_RETRIES ]; then
      echo "Waiting $RETRY_INTERVAL seconds before retrying..."
      sleep $RETRY_INTERVAL
    fi
  fi
done

if [ $SUCCESS -eq 0 ]; then
  echo "[ERROR]: Poetry install failed after $MAX_RETRIES attempts. Check your network or Poetry configuration."
  exit 1
fi

echo "Linting the source code..."
poetry run flake8 src/ --count --select=E,F,W --show-source --statistics || {
  echo "Linting issues have been identified, the commit is blocked. See details above."
  exit 1
}

echo "Running security scans..."
poetry run bandit -r src/ -ll || {
  echo "Security issues have been identified, the commit is blocked. See details above."
  exit 1
}

exit 0
EOF

chmod +x .git/hooks/pre-commit
