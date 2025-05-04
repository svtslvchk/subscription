from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import uuid

from app.database import get_db
from app.models import Payment, UserSubscription, Subscription, User, Notification
from app.auth import get_current_user
from app.schemas import PaymentCreate, PaymentOut

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


# Вспомогательные функции
def process_payment(amount: float, method: str) -> dict:
    return {
        "status": "completed",
        "transaction_id": f"pay_{uuid.uuid4()}"
    }


def create_notification(db: Session, user_id: int, message: str, type: str):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=type,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    return notification


# Роутеры
@router.post("/", response_model=PaymentOut)
async def create_payment(
        payment_data: PaymentCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # Проверка подписки
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.subscription_id == payment_data.subscription_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Проверка баланса
    if payment_data.payment_method == "balance" and user.balance < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Обработка платежа
    payment_result = process_payment(payment_data.amount, payment_data.payment_method)

    # Списание средств
    if payment_result["status"] == "completed":
        if payment_data.payment_method == "balance":
            user.balance -= payment_data.amount

        # Обновление подписки
        if subscription.end_date < datetime.utcnow().date():
            sub_info = db.query(Subscription).get(payment_data.subscription_id)
            subscription.start_date = datetime.utcnow().date()
            subscription.end_date = datetime.utcnow().date() + timedelta(days=sub_info.duration_days)
        subscription.is_active = True

    # Создание платежа
    payment = Payment(
        user_id=user.id,
        subscription_id=payment_data.subscription_id,
        amount=payment_data.amount,
        status=payment_result["status"],
        payment_method=payment_data.payment_method,
        external_id=payment_result["transaction_id"],
        created_at=datetime.utcnow()
    )

    # Уведомление
    create_notification(
        db,
        user.id,
        f"Payment {payment_data.amount} RUB for subscription #{payment_data.subscription_id}",
        "payment"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentOut])
async def get_payments(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    return db.query(Payment) \
        .filter(Payment.user_id == user.id) \
        .offset(skip) \
        .limit(limit) \
        .all()