import asyncio
import base64
import os
import threading
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
from hvac import Client as VaultSDKClient
from sqlcipher3 import dbapi2 as sqlite

VAULT_BASE_URL = os.environ.get("VAULT_ADDR")
VAULT_TOKEN = os.environ.get("VAULT_TOKEN")

CONJUR_BASE_URL = os.environ.get("CONJUR_BASE_URL", "http://conjur:80")
ACCOUNT = os.environ.get("CONJUR_ACCOUNT", "movienight")
SQLITE_POLICY = "sqlite-policy"
CONJUR_LOGIN_FOR_PROXY = os.environ.get("CONJUR_LOGIN_FOR_PROXY", f"host/{SQLITE_POLICY}/database-proxy")
CONJUR_CERT_FILE = os.environ.get("CONJUR_CERT_FILE")

CONJUR_TOKEN_FILE = Path(__file__).resolve().parent / "conjur_token"
SQLITE_SECRET_PATH = "sqlite/key"
VAULT_ACCESS_PATH = f"{ACCOUNT}/{SQLITE_SECRET_PATH}"


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result = {}
    error = {}

    def runner():
        try:
            result["value"] = asyncio.run(coro)
        except Exception as exc:
            error["exc"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()

    if "exc" in error:
        raise error["exc"]

    return result["value"]


def init_encryption_key():
    vault_client = VaultSDKClient(url=VAULT_BASE_URL, token=VAULT_TOKEN)

    if not vault_client.is_authenticated():
        raise RuntimeError("Vault auth failed")

    response = vault_client.secrets.transit.generate_random_bytes(n_bytes=32)
    raw_key = response["data"]["random_bytes"]

    if isinstance(raw_key, str):
        raw_key = raw_key.encode("utf-8")
    elif isinstance(raw_key, bytes):
        raw_key = raw_key
    else:
        raise TypeError(f"Unexpected type for random_bytes: {type(raw_key)}")

    encryption_key = base64.b64encode(raw_key).decode("utf-8")
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=VAULT_ACCESS_PATH,
        secret={"encryption_key": encryption_key},
        mount_point="secret"
    )

    conjur_client = ConjurClient()
    conjur_client.set_encryption_key(encryption_key)


class ConjurClient:
    def __init__(self):
        conjur_token = CONJUR_TOKEN_FILE.read_text(encoding="utf-8").strip()

        if not CONJUR_BASE_URL:
            raise RuntimeError("CONJUR_BASE_URL is not set")
        if not ACCOUNT:
            raise RuntimeError("CONJUR_ACCOUNT is not set")

        connection_info = ConjurConnectionInfo(
            conjur_url=CONJUR_BASE_URL,
            account=ACCOUNT,
            cert_file=CONJUR_CERT_FILE,
            service_id=None,
            proxy_params=None,
        )

        credentials = CredentialsData(
            username=CONJUR_LOGIN_FOR_PROXY,
            api_key=conjur_token,
            machine=CONJUR_BASE_URL,
        )

        credentials_provider = SimpleCredentialsProvider()
        credentials_provider.save(credentials)

        authn_provider = AuthnAuthenticationStrategy(credentials_provider)

        ssl_mode = (
            SslVerificationMode.SELF_SIGN
            if CONJUR_CERT_FILE
            else SslVerificationMode.TRUST_STORE
        )

        self.client = ConjurSDKClient(
            connection_info,
            authn_strategy=authn_provider,
            ssl_verification_mode=ssl_mode,
        )

        self.variable_id = f"{SQLITE_POLICY}/{SQLITE_SECRET_PATH}"

    def get_encryption_key(self) -> str:
        value = _run_async(self.client.get(self.variable_id))
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def set_encryption_key(self, encryption_key: str):
        _run_async(self.client.set(self.variable_id, encryption_key))


class EncryptedSQLiteClient:
    def __init__(self, db_path: str):
        self.key_provider = ConjurClient()
        self.db_path = db_path

    def connect(self) -> sqlite.Connection:
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite.connect(str(db_path))
        key = self.key_provider.get_encryption_key().strip()

        connection.executescript(f"""
        PRAGMA key = "x'{key}'";
        PRAGMA cipher_compatibility = 4;
        PRAGMA cipher_memory_security = ON;
        """)

        return connection