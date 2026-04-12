from movienight.api.openapi_operation_patcher import (
    patch_operation_responses,
)


def patch_path_item(path_item: dict) -> None:
    for operation in path_item.values():
        if isinstance(operation, dict):
            patch_operation_responses(operation)
