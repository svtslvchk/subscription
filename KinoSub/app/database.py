from sqlalchemy import create_engine #создает подключение к бд
from sqlalchemy.orm import sessionmaker #создает новые сессии, основной способ взаимодействия с бд в орм режиме
from app.config import DATABASE_URL #наш url, через который осуществляется подключение к бд
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(DATABASE_URL) #подключаемся к бд

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #создаем фабрику сессий (генератор сессий для запросов)

def get_db(): #создаем сессию, затем передаем управление вызывающему коду, после выполнения которого, закрываем бд
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
