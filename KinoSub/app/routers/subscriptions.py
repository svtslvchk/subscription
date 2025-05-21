from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Subscription
from app.schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionOut
from app.dependencies.roles import require_admin  # новая зависимость

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)

@router.post("/", response_model=SubscriptionOut)
def create_subscription(
        subscription: SubscriptionCreate,
        db: Session = Depends(get_db),
        admin: str = Depends(require_admin)  # ограничение
):
    if subscription.discount_rate and not subscription.discount_until:
        raise HTTPException(status_code=400, detail="Для скидки укажите discount_until")

    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.put("/{subscription_id}", response_model=SubscriptionOut)
def update_subscription(
        subscription_id: int,
        subscription: SubscriptionUpdate,
        db: Session = Depends(get_db),
        admin: str = Depends(require_admin)  # ограничение
):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    for key, value in subscription.dict(exclude_unset=True).items():
        setattr(db_subscription, key, value)

    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.delete("/{subscription_id}")
def delete_subscription(
        subscription_id: int,
        db: Session = Depends(get_db),
        admin: str = Depends(require_admin)  # ограничение
):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    db.delete(db_subscription)
    db.commit()
    return {"message": "Подписка удалена"}

@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(skip: int = 0, limit: int = 100, active_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Subscription)
    if active_only:
        query = query.filter(Subscription.is_active == True)
    return query.offset(skip).limit(limit).all()

@router.get("/{subscription_id}", response_model=SubscriptionOut)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    return subscription

