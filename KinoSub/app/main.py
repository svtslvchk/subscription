from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers import users, subscriptions, user_subscriptions, payments, wallet, notifications, auth, debug_admin, subscription_requests

app = FastAPI()

# Подключение роутеров
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(user_subscriptions.router)
app.include_router(payments.router)
app.include_router(wallet.router)
app.include_router(notifications.router)
app.include_router(auth.router)
app.include_router(debug_admin.router)
app.include_router(subscription_requests.router)

@app.get("/")
def root():
    return {"message": "Добро пожаловать в кинотеатр!"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="KinoSub API",
        version="1.0.0",
        description="API для кинотеатра",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2Password": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/token",
                    "scopes": {}
                }
            }
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"OAuth2Password": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema
