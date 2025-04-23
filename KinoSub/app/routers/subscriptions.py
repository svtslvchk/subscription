from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Subscription
from app.schemas import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionOut
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)


# Создание подписки (CREATE)
@router.post("/", response_model=SubscriptionOut)
def create_subscription(
        subscription: SubscriptionCreate,
        db: Session = Depends(get_db)
):
    # Проверка, что скидка указана с датой окончания
    if subscription.discount_rate is not None and subscription.discount_until is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для скидки укажите discount_until"
        )

    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


# Получение всех подписок (READ ALL)
@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        db: Session = Depends(get_db)
):
    query = db.query(Subscription)
    if active_only:
        query = query.filter(Subscription.is_active == True)
    return query.offset(skip).limit(limit).all()


# Получение подписки по ID (READ ONE)
@router.get("/{subscription_id}", response_model=SubscriptionOut)
def get_subscription(
        subscription_id: int,
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    return subscription


# Обновление подписки (UPDATE)
@router.put("/{subscription_id}", response_model=SubscriptionOut)
def update_subscription(
        subscription_id: int,
        subscription: SubscriptionUpdate,
        db: Session = Depends(get_db)
):
    db_subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    # Обновляем только переданные поля
    update_data = subscription.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subscription, key, value)

    db.commit()
    db.refresh(db_subscription)
    return db_subscription


# Удаление подписки (DELETE)
@router.delete("/{subscription_id}")
def delete_subscription(
        subscription_id: int,
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    db.delete(subscription)
    db.commit()
    return {"message": "Подписка удалена"}