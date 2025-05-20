from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/subscriptions", response_class=HTMLResponse)
def serve_subscriptions(request: Request):
    return templates.TemplateResponse("subscriptions.html", {"request": request})

@router.get("/wallet", response_class=HTMLResponse)
def serve_wallet(request: Request):
    return templates.TemplateResponse("wallet.html", {"request": request})

# Можно добавить ещё: /history, /admin и т.д.
