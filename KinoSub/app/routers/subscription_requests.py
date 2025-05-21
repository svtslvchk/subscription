from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import SubscriptionRequest, User, UserSubscription, Subscription
from app.auth import get_current_user, get_admin_user
from app.schemas import SubscriptionRequestCreate, SubscriptionRequestOut

router = APIRouter(
    prefix="/subscription-requests",
    tags=["subscription-requests"]
)

# Пользователь делает запрос на подписку
@router.post("/", response_model=SubscriptionRequestOut)
def create_subscription_request(
    request_data: SubscriptionRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка, не существует ли уже активной подписки
    existing = db.query(SubscriptionRequest).filter_by(
        user_id=current_user.id,
        subscription_id=request_data.subscription_id,
        status="pending"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Запрос уже отправлен и ожидает обработки")

    subscription = db.query(Subscription).get(request_data.subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    new_request = SubscriptionRequest(
        user_id=current_user.id,
        subscription_id=request_data.subscription_id,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


# Админ получает список всех заявок
@router.get("/admin", response_model=List[SubscriptionRequestOut])
def get_all_requests(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    return db.query(SubscriptionRequest).order_by(SubscriptionRequest.created_at.desc()).all()


# Админ одобряет заявку
@router.patch("/admin/{request_id}/approve", response_model=SubscriptionRequestOut)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    req = db.query(SubscriptionRequest).get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    # Проверка, не существует ли уже подписки
    existing_sub = db.query(UserSubscription).filter_by(
        user_id=req.user_id,
        subscription_id=req.subscription_id
    ).first()

    if not existing_sub:
        new_sub = UserSubscription(
            user_id=req.user_id,
            subscription_id=req.subscription_id,
            start_date=datetime.utcnow().date(),
            end_date=None,
            is_active=False  # активной станет после оплаты
        )
        db.add(new_sub)

    req.status = "approved"
    db.commit()
    db.refresh(req)
    return req


# Админ отклоняет заявку
@router.patch("/admin/{request_id}/reject", response_model=SubscriptionRequestOut)
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    req = db.query(SubscriptionRequest).get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    req.status = "rejected"
    db.commit()
    db.refresh(req)
    return req
