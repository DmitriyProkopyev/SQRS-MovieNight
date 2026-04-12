from movienight.api.openapi_path_patcher import patch_path_item


def patch_validation_responses(schema: dict) -> None:
    for path_item in schema.get("paths", {}).values():
        patch_path_item(path_item)
