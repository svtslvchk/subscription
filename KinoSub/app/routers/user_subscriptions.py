from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
from app.models import UserSubscription, User, Subscription
from app.schemas import UserSubscriptionOut, UserSubscriptionCreate
from app.database import get_db

router = APIRouter(
    prefix="/user-subscriptions",
    tags=["user_subscriptions"]
)

@router.post("/", response_model=UserSubscriptionOut)
def assign_subscription(
    subscription: UserSubscriptionCreate,
    db: Session = Depends(get_db)
):
    # Проверяем, есть ли пользователь и подписка
    db_user = db.query(User).filter(User.id == subscription.user_id).first()
    db_sub = db.query(Subscription).filter(Subscription.id == subscription.subscription_id).first()

    if not db_user or not db_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь или подписка не найдены"
        )

    # Рассчитываем end_date, если не указан (на основе duration_days из подписки)
    if not subscription.end_date:
        end_date = date.today() + timedelta(days=db_sub.duration_days)
    else:
        end_date = subscription.end_date

    # Создаем запись
    db_user_sub = UserSubscription(
        user_id=subscription.user_id,
        subscription_id=subscription.subscription_id,
        start_date=date.today(),
        end_date=end_date,
        is_active=True,
        auto_renew=subscription.auto_renew
    )

    db.add(db_user_sub)
    db.commit()
    db.refresh(db_user_sub)
    return db_user_sub

@router.get("/user/{user_id}", response_model=List[UserSubscriptionOut])
def get_user_subscriptions(
    user_id: int,
    db: Session = Depends(get_db)
):
    subscriptions = db.query(UserSubscription)\
        .filter(UserSubscription.user_id == user_id)\
        .all()
    return subscriptions

@router.patch("/{subscription_id}/renew", response_model=UserSubscriptionOut)
def renew_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    user_sub = db.query(UserSubscription)\
        .filter(UserSubscription.id == subscription_id)\
        .first()

    if not user_sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    # Продлеваем подписку на duration_days из связанной подписки
    sub = db.query(Subscription)\
        .filter(Subscription.id == user_sub.subscription_id)\
        .first()

    user_sub.end_date = user_sub.end_date + timedelta(days=sub.duration_days)
    user_sub.is_active = True
    db.commit()
    return user_sub