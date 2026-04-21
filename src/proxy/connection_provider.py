import os

from conjur_api import Client as ConjurSDKClient
from hvac import Client as VaultSDKClient
from pathlib import Path
from sqlcipher3 import dbapi2 as sqlite


VAULT_BASE_URL = os.environ.get("VAULT_ADDR")
VAULT_TOKEN = os.environ.get("VAULT_TOKEN")

CONJUR_BASE_URL = "https://conjur:3000"
CONJUR_ACCOUNT = "movienight"
CONJUR_LOGIN_FOR_PROXY = "host/database-proxy"
CONJUR_TOKEN_FILE = Path(__file__).resolve().parent / "conjur_token"

SQLITE_SECRET_PATH = 'sqlite/key'
SQLITE_POLICY = 'sqlite-policy'


def init_encryption_key():
    vault_client = VaultSDKClient(url=VAULT_BASE_URL, token=VAULT_TOKEN)
    
    response = vault_client.secrets.transit.generate_random_bytes(n_bytes=32)
    encryption_key = response['data']['random_bytes'].hex()
    
    conjur_client = ConjurClient()
    conjur_client.set_encryption_key(encryption_key)


class ConjurClient:
    def __init__(self):
        conjur_token = CONJUR_TOKEN_FILE.read_text(encoding='utf-8').strip()
        self.client = ConjurSDKClient(
            url=CONJUR_BASE_URL,
            account=CONJUR_ACCOUNT,
            login_id=CONJUR_LOGIN_FOR_PROXY,
            api_key=conjur_token
        )
        self.resource_id = f"{CONJUR_ACCOUNT}:{SQLITE_POLICY}/{SQLITE_SECRET_PATH}"

    def get_encryption_key(self) -> str:
        full_id = f"variable:{self.resource_id}"
        key_bytes = self.client.get(full_id)
        return key_bytes.decode('utf-8')

    def set_encryption_key(self, encryption_key: str):
        full_id = f"variable:{self.resource_id}"
        self.client.set(full_id, encryption_key)


class EncryptedSQLiteClient:
    def __init__(self, db_path: str):
        self.key_provider = ConjurClient()
        self.db_path = db_path

    def connect(self) -> sqlite.Connection:
        """Return sqlite3-compatible connection to encrypted DB."""
        connection = sqlite.connect(self.db_path)
        key = self.key_provider.get_encryption_key()
        
        connection.execute("PRAGMA key = ?", (key,))
        connection.execute("PRAGMA cipher_compatibility = 4")
        connection.execute("PRAGMA cipher_memory_security = ON")
        
        return connection
