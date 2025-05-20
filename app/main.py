from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.responses import FileResponse

from app.routers import (
    auth,
    users,
    subscriptions,
    payments,
    user_subscriptions,
    notifications,
    debug_admin,
)
from app.frontend import router as frontend_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно ограничить доменом
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(user_subscriptions.router)
app.include_router(notifications.router)
app.include_router(debug_admin.router)
app.include_router(frontend_router)

# Статика и шаблоны — указываем полный путь относительно корня проекта
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Если используете шаблоны Jinja2 (в будущем), подключите так (пример):
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=FileResponse)
def read_root():
    # Возвращаем файл index.html из папки templates
    return FileResponse("app/templates/index.html")
