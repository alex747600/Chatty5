from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers.subscriptions import router as subscriptions_router

app = FastAPI()

# Подключаем роутеры
app.include_router(subscriptions_router)

# --- Добавляем Security схему для Bearer Token ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Subscription Service",
        version="1.0.0",
        description="API for subscriptions and feed",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

