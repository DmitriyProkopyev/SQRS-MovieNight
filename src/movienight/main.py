from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from movienight.api.router import api_router
from movienight.core.config import settings
from movienight.db.init_db import initialize_database

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Movie Night backend API. "
        "Use /api/v1/auth/login to get a JWT token. "
        "Then use the token for protected endpoints or in the Streamlit GUI."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses", {})

            if "400" not in responses:
                responses["400"] = {
                    "description": (
                        "Bad Request. Validation failed "
                        "for request path, "
                        "query parameters, or body."
                    ),
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": [
                                    {
                                        "type": "string_too_short",
                                        "loc": ["body", "username"],
                                        "msg": (
                                            "String should have "
                                            "at least 3 characters"
                                        ),
                                        "input": "",
                                        "ctx": {"min_length": 3},
                                    }
                                ]
                            }
                        }
                    },
                }
            else:
                existing_400 = responses["400"]
                existing_400.setdefault(
                    "description",
                    "Bad Request. Validation "
                    "failed for request path, "
                    "query parameters, or body.",
                )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get(
    "/",
    summary="Root endpoint",
    description="Return basic information about the API service.",
    response_model=dict,
    tags=["system"],
)
def root() -> dict[str, str]:
    return {
        "service": "movie-night-api",
        "status": "ok",
    }


@app.get(
    "/health",
    summary="Health check",
    description="Return a simple health status for the backend service.",
    response_model=dict,
    tags=["system"],
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def run() -> None:
    import uvicorn

    uvicorn.run(
        "movienight.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
