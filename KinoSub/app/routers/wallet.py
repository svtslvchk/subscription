from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation

from app.database import get_db
from app.models import User
from app.schemas import BalanceUpdate
from app.auth import get_current_user

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)

@router.get("/balance", response_model=float)
async def get_user_balance(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить текущий баланс пользователя
    """
    return float(current_user.balance or 0)


@router.post("/topup", status_code=status.HTTP_200_OK)
async def top_up_balance(
        balance_data: BalanceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Пополнить баланс пользователя
    """
    try:
        amount = Decimal(str(balance_data.amount))
    except (InvalidOperation, TypeError):
        raise HTTPException(status_code=400, detail="Некорректная сумма")

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма пополнения должна быть больше 0"
        )

    if current_user.balance is None:
        current_user.balance = Decimal("0")

    current_user.balance += amount
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Баланс успешно пополнен",
        "new_balance": float(current_user.balance)
    }


@router.post("/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_from_balance(
        balance_data: BalanceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Списать средства с баланса
    """
    try:
        amount = Decimal(str(balance_data.amount))
    except (InvalidOperation, TypeError):
        raise HTTPException(status_code=400, detail="Некорректная сумма")

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма списания должна быть больше 0"
        )

    if current_user.balance is None:
        current_user.balance = Decimal("0")

    if current_user.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств на балансе"
        )

    current_user.balance -= amount
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Средства успешно списаны",
        "new_balance": float(current_user.balance)
    }


@router.get("/history")
async def get_balance_history(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить историю операций с балансом
    """
    return {"message": "История операций будет реализована позже"}
