from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from movienight.api.openapi_response_patcher import (
    patch_validation_responses,
)


def build_custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    patch_validation_responses(schema)

    app.openapi_schema = schema
    return schema
