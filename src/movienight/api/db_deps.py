from typing import Annotated

from fastapi import Depends

from movienight.integrations.sqlite_proxy_client import SQLiteProxyClient


def get_db() -> SQLiteProxyClient:
    return SQLiteProxyClient()


DbSession = Annotated[SQLiteProxyClient, Depends(get_db)]