# app/utilities/openapi.py
from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API description",
        routes=app.routes,
    )
    # Remove specific schemas from the OpenAPI documentation if they exist
    if "components" in openapi_schema:
        if "schemas" in openapi_schema["components"]:
            schemas_to_remove = [
                "Body_authenticate_auth_token_post",
                # "HTTPValidationError",
                "RoleEnum",
                "UserRequest",
                "UserUpdateRequest",
                "ValidationError",
                "WalletCreationRequest",
                "WalletInfoResponse",
                "WalletUpdateRequest",
                # "MessageResponse",
                # "TransactionRequest",
                # "TransactionResponse"
            ]
            for schema in schemas_to_remove:
                openapi_schema["components"]["schemas"].pop(schema, None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema
