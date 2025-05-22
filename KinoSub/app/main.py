from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import auth, users, subscriptions, wallet, payments, user_subscriptions, subscription_requests, notifications, debug_admin
import os

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(wallet.router)
app.include_router(payments.router)
app.include_router(user_subscriptions.router)
app.include_router(subscription_requests.router)
app.include_router(notifications.router)
app.include_router(debug_admin.router)

# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="app/static"), name="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/notifications.html", response_class=HTMLResponse)
async def notifications_page(request: Request):
    return templates.TemplateResponse("notifications.html", {"request": request})
