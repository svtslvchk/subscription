from fastapi import FastAPI
from app.routers import users, subscriptions, user_subscriptions, payments, wallet, notifications, auth  # Импортируем роутер

app = FastAPI()

# Подключаем роутер
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(user_subscriptions.router)
app.include_router(payments.router)
app.include_router(wallet.router)
app.include_router(notifications.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Добро пожаловать в кинотеатр!"}
