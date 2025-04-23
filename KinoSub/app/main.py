from fastapi import FastAPI
from app.routers import users, subscriptions, user_subscriptions  # Импортируем роутер

app = FastAPI()

# Подключаем роутер
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(user_subscriptions.router)


@app.get("/")
def root():
    return {"message": "Добро пожаловать в кинотеатр!"}
