from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List

from app.models import UserSubscription, User, Subscription
from app.schemas import UserSubscriptionOut, UserSubscriptionCreate
from app.database import get_db
from app.auth import get_current_user, get_current_admin_user  # 🔒 добавлено

router = APIRouter(
    prefix="/user-subscriptions",
    tags=["user_subscriptions"]
)

# 👇 Только админ может вручную назначить подписку пользователю
@router.post("/", response_model=UserSubscriptionOut, status_code=status.HTTP_201_CREATED)
def assign_subscription_to_self(
    subscription_data: UserSubscriptionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    db_sub = db.query(Subscription).get(subscription_data.subscription_id)

    if not db_sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    existing = db.query(UserSubscription).filter_by(
        user_id=admin.id,
        subscription_id=subscription_data.subscription_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="У вас уже есть эта подписка")

    end_date = date.today() + timedelta(days=db_sub.duration_days)

    new_sub = UserSubscription(
        user_id=admin.id,
        subscription_id=subscription_data.subscription_id,
        start_date=date.today(),
        end_date=end_date,
        is_active=True,
        auto_renew=subscription_data.auto_renew
    )

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

# 👇 Доступ к своим подпискам — для обычных пользователей
@router.get("/me", response_model=List[UserSubscriptionOut])
def get_my_subscriptions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    subscriptions = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id
    ).all()

    today = date.today()
    for sub in subscriptions:
        if sub.end_date and sub.end_date < today:
            sub.is_active = False

    db.commit()
    return subscriptions


# 👇 Продление подписки — либо админ, либо владелец
@router.patch("/{subscription_id}/renew", response_model=UserSubscriptionOut)
def renew_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user_sub = db.query(UserSubscription).filter(
        UserSubscription.id == subscription_id
    ).first()

    if not user_sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    if user_sub.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа к продлению чужой подписки")

    sub = db.query(Subscription).filter(Subscription.id == user_sub.subscription_id).first()

    user_sub.end_date += timedelta(days=sub.duration_days)
    user_sub.is_active = True
    db.commit()
    return user_sub
