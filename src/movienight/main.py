from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from movienight.api.openapi_customizer import build_custom_openapi
from movienight.api.router import api_router
from movienight.api.validation_error_handler import request_validation_exception_handler
from movienight.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Movie Night backend API. "
        "Use /api/v1/auth/login to get a JWT "
        "token, then use it for protected endpoints or in Streamlit."
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
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,
)


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


def custom_openapi():
    return build_custom_openapi(app)


app.openapi = custom_openapi


def run() -> None:
    import uvicorn

    uvicorn.run(
        "movienight.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )