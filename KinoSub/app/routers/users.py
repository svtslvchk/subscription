from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# добавление пользователя
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создание пользователя с хешированием пароля"""
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email или username уже заняты"
        )

    # Хешируем пароль перед сохранением
    hashed_password = pwd_context.hash(user.password)

    # Создаём пользователя
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,  # Сохраняем хеш, а не пароль!
        role="user",
        balance=0,
        created_at=datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Пагинация: пропуск записей"),
    limit: int = Query(100, description="Пагинация: лимит записей")
):
    """Получение списка пользователей с пагинацией"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновление пользователя (с проверкой пароля)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Обновляем только переданные поля
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.password:  # Если пароль передан — хешируем его
        user.password_hash = pwd_context.hash(user_data.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    db.delete(user)
    db.commit()
    return  # 204 No Content