"""Demo: fetch the SQLCipher encryption key from Conjur Open Source via the
official Python SDK (`conjur-api`).

This script exercises the same authentication path the SQLite proxy takes
at runtime (see `src/proxy/connection_provider.py:ConjurClient`), but
runs standalone from the host so it can be demonstrated without entering
the proxy container.

It reads:
  - Conjur connection settings from environment (defaults match .env.example)
  - The proxy's API token from `src/proxy/conjur_token`

Run with:
    poetry run python scripts/demo_get_key.py

Expected output: the 32-byte hex SQLCipher key currently held by Conjur.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from conjur_api import Client as ConjurSDKClient
from conjur_api.models import (
    ConjurConnectionInfo,
    CredentialsData,
    SslVerificationMode,
)
from conjur_api.providers import (
    AuthnAuthenticationStrategy,
    SimpleCredentialsProvider,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONJUR_TOKEN_FILE = REPO_ROOT / "src" / "proxy" / "conjur_token"

VARIABLE_ID = "sqlite-policy/sqlite/key"

CONJUR_BASE_URL = os.environ.get("CONJUR_BASE_URL", "https://localhost:8443")
CONJUR_ACCOUNT = os.environ.get("CONJUR_ACCOUNT", "myConjurAccount")
CONJUR_LOGIN = os.environ.get(
    "CONJUR_LOGIN_FOR_PROXY",
    "host/sqlite-policy/database-proxy",
)
CONJUR_CERT_FILE = os.environ.get(
    "CONJUR_CERT_FILE",
    str(REPO_ROOT / "infra" / "conjur" / "conf" / "tls" / "nginx.crt"),
)


def load_api_token() -> str:
    if not CONJUR_TOKEN_FILE.exists():
        sys.exit(
            f"error: {CONJUR_TOKEN_FILE} does not exist. "
            "Run infra/conjur/bootstrap.sh first."
        )
    token = CONJUR_TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not token or token.upper().startswith("PUT UR TOKEN"):
        sys.exit(
            f"error: {CONJUR_TOKEN_FILE} contains a placeholder. "
            "Run infra/conjur/bootstrap.sh to populate it."
        )
    return token


def build_client() -> ConjurSDKClient:
    api_token = load_api_token()

    connection_info = ConjurConnectionInfo(
        conjur_url=CONJUR_BASE_URL,
        account=CONJUR_ACCOUNT,
        cert_file=CONJUR_CERT_FILE if Path(CONJUR_CERT_FILE).exists() else None,
        service_id=None,
        proxy_params=None,
    )

    credentials = CredentialsData(
        username=CONJUR_LOGIN,
        api_key=api_token,
        machine=CONJUR_BASE_URL,
    )
    credentials_provider = SimpleCredentialsProvider()
    credentials_provider.save(credentials)

    ssl_mode = (
        SslVerificationMode.SELF_SIGN
        if Path(CONJUR_CERT_FILE).exists()
        else SslVerificationMode.TRUST_STORE
    )

    return ConjurSDKClient(
        connection_info,
        authn_strategy=AuthnAuthenticationStrategy(credentials_provider),
        ssl_verification_mode=ssl_mode,
    )


async def fetch_key() -> str:
    client = build_client()
    value = await client.get(VARIABLE_ID)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def main() -> None:
    print(f"==> conjur-api SDK fetch: {VARIABLE_ID}")
    print(f"    url:     {CONJUR_BASE_URL}")
    print(f"    account: {CONJUR_ACCOUNT}")
    print(f"    login:   {CONJUR_LOGIN}")
    print()
    key = asyncio.run(fetch_key())
    print(key)


if __name__ == "__main__":
    main()
