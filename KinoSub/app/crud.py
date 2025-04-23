from sqlalchemy.orm import Session
from models import User, Subscription, Wallet, Payment, UserSubscription
from typing import Optional, List
from datetime import datetime, timedelta
import pytz


# =============================================
# CRUD операции для пользователей (User)
# =============================================

def create_user(db: Session, user_data):
    """Создание нового пользователя"""
    db_user = User(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    """Обновление данных пользователя"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Удаление пользователя"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# =============================================
# CRUD операции для подписок (Subscription)
# =============================================

def create_subscription(db: Session, subscription_data):
    """Создание новой подписки"""
    db_sub = Subscription(**subscription_data.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    """Получение подписки по ID"""
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
    """Получение списка подписок с пагинацией"""
    return db.query(Subscription).offset(skip).limit(limit).all()


def update_subscription(db: Session, subscription_id: int, update_data: dict) -> Optional[Subscription]:
    """Обновление данных подписки"""
    db_sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_sub:
        for key, value in update_data.items():
            setattr(db_sub, key, value)
        db.commit()
        db.refresh(db_sub)
    return db_sub


def deactivate_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    """Деактивация подписки (мягкое удаление)"""
    db_sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_sub:
        db_sub.is_active = False
        db.commit()
        db.refresh(db_sub)
    return db_sub


# =============================================
# CRUD операции для кошельков (Wallet)
# =============================================

def create_wallet(db: Session, user_id: int) -> Wallet:
    """Создание кошелька для пользователя"""
    db_wallet = Wallet(user_id=user_id, balance=0.0)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


def get_wallet(db: Session, user_id: int) -> Optional[Wallet]:
    """Получение кошелька пользователя"""
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()


def update_wallet_balance(db: Session, user_id: int, amount: float) -> Optional[Wallet]:
    """Обновление баланса кошелька"""
    db_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if db_wallet:
        db_wallet.balance += amount
        db.commit()
        db.refresh(db_wallet)
    return db_wallet


# =============================================
# CRUD операции для платежей (Payment)
# =============================================

def create_payment(db: Session, payment_data) -> Payment:
    """Создание записи о платеже"""
    db_payment = Payment(**payment_data.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Получение платежей пользователя"""
    return db.query(Payment).filter(Payment.user_id == user_id).offset(skip).limit(limit).all()


def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    """Получение платежа по ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()


# =============================================
# CRUD операции для подписок пользователей (UserSubscription)
# =============================================

def create_user_subscription(db: Session, user_sub_data) -> UserSubscription:
    """Активация подписки для пользователя"""
    # Вычисляем дату следующего платежа
    subscription = get_subscription(db, user_sub_data.subscription_id)
    next_payment = datetime.now(pytz.utc) + timedelta(days=subscription.duration_days)

    db_user_sub = UserSubscription(
        user_id=user_sub_data.user_id,
        subscription_id=user_sub_data.subscription_id,
        next_payment_date=next_payment,
        is_active=True
    )
    db.add(db_user_sub)
    db.commit()
    db.refresh(db_user_sub)
    return db_user_sub


def get_user_subscriptions(db: Session, user_id: int) -> List[UserSubscription]:
    """Получение активных подписок пользователя"""
    return db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == True
    ).all()


def deactivate_user_subscription(db: Session, user_sub_id: int) -> Optional[UserSubscription]:
    """Деактивация подписки пользователя"""
    db_user_sub = db.query(UserSubscription).filter(UserSubscription.id == user_sub_id).first()
    if db_user_sub:
        db_user_sub.is_active = False
        db.commit()
        db.refresh(db_user_sub)
    return db_user_sub

# Операции для UserSubscription
def create_user_subscription(db: Session, user_sub_data):
    db_user_sub = UserSubscription(**user_sub_data.dict())
    db.add(db_user_sub)
    db.commit()
    db.refresh(db_user_sub)
    return db_user_sub

def get_user_subscriptions(db: Session, user_id: int):
    return db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == True
    ).all()

# Для платежей
def get_payments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Payment)\
        .filter(Payment.user_id == user_id)\
        .order_by(Payment.created_at.desc())\
        .offset(skip).limit(limit).all()

# Для кошелька
def update_wallet_balance(db: Session, user_id: int, amount: float):
    db_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if db_wallet:
        db_wallet.balance += amount
        db.commit()
        db.refresh(db_wallet)
    return db_wallet