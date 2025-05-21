from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from decimal import Decimal
import uuid

from app.database import get_db
from app.models import (
    Payment,
    UserSubscription,
    Subscription,
    User,
    Notification,
    BalanceTransaction,
)
from app.auth import get_current_user
from app.schemas import PaymentCreate, PaymentOut, RefundRequest, AutoRenewUpdate

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


def process_payment(amount: Decimal, method: str) -> dict:
    return {
        "status": "completed",
        "transaction_id": f"pay_{uuid.uuid4()}"
    }


def create_notification(db: Session, user_id: int, message: str):
    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    return notification


@router.post("/", response_model=PaymentOut)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        amount = Decimal(str(payment_data.amount))

        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user.id,
            UserSubscription.subscription_id == payment_data.subscription_id
        ).first()

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not assigned")

        if payment_data.payment_method == "balance" and user.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        payment_result = process_payment(amount, payment_data.payment_method)

        if payment_result["status"] == "completed":
            if payment_data.payment_method == "balance":
                user.balance -= amount
                transaction = BalanceTransaction(
                    user_id=user.id,
                    amount=amount,
                    type="withdraw",
                    description=f"Оплата подписки #{payment_data.subscription_id}"
                )
                db.add(transaction)

            if not subscription.end_date or subscription.end_date < datetime.utcnow().date():
                sub_info = db.query(Subscription).get(payment_data.subscription_id)
                subscription.start_date = datetime.utcnow().date()
                subscription.end_date = datetime.utcnow().date() + timedelta(days=sub_info.duration_days)

            subscription.is_active = True

        payment = Payment(
            user_id=user.id,
            subscription_id=payment_data.subscription_id,
            amount=amount,
            status=payment_result["status"],
            payment_method=payment_data.payment_method,
            external_id=payment_result["transaction_id"],
            created_at=datetime.utcnow()
        )
        db.add(payment)

        create_notification(
            db,
            user.id,
            f"Оплата {amount}₽ за подписку #{payment_data.subscription_id}"
        )

        db.commit()
        db.refresh(payment)
        return payment

    except Exception:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при создании платежа")


@router.get("/", response_model=List[PaymentOut])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Payment)\
        .filter(Payment.user_id == user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()


@router.post("/{payment_id}/refund", response_model=PaymentOut)
async def refund_payment(
    payment_id: int,
    refund: RefundRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user.id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")

    if payment.status != "completed" or payment.is_refunded:
        raise HTTPException(status_code=400, detail="Платёж уже возвращён или не был успешным")

    user.balance += payment.amount

    transaction = BalanceTransaction(
        user_id=user.id,
        amount=payment.amount,
        type="topup",
        description=f"Возврат по платежу #{payment.id}"
    )
    db.add(transaction)

    payment.is_refunded = True
    payment.refund_reason = refund.reason
    payment.status = "refunded"

    subscription = db.query(UserSubscription).filter_by(
        user_id=user.id,
        subscription_id=payment.subscription_id
    ).first()

    if subscription:
        subscription.is_active = False
        subscription.end_date = datetime.utcnow().date()

    create_notification(
        db,
        user.id,
        f"Произведён возврат {payment.amount}₽ по платежу #{payment.id}"
    )

    db.commit()
    db.refresh(payment)
    return payment


@router.patch("/subscriptions/{subscription_id}/auto-renew")
def toggle_auto_renew(
    subscription_id: int,
    data: AutoRenewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    usub = db.query(UserSubscription).filter_by(
        user_id=user.id,
        subscription_id=subscription_id
    ).first()

    if not usub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    usub.auto_renew = data.enable
    db.commit()
    return {"subscription_id": subscription_id, "auto_renew": usub.auto_renew}
