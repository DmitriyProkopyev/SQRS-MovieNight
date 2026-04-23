from fastapi import FastAPI

from proxy.api.router import router
from proxy.db.init_db import initialize_database

app = FastAPI(title="sqlite-proxy", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}