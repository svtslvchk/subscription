from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    return current_user.balance


@router.post("/topup", status_code=status.HTTP_200_OK)
async def top_up_balance(
        balance_data: BalanceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Пополнить баланс пользователя
    """
    if balance_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма пополнения должна быть больше 0"
        )

    current_user.balance += balance_data.amount
    db.commit()

    # Здесь можно добавить запись в историю операций
    # и отправку уведомления

    return {"message": "Баланс успешно пополнен", "new_balance": current_user.balance}


@router.post("/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_from_balance(
        balance_data: BalanceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Списать средства с баланса (для оплаты подписки)
    """
    if balance_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма списания должна быть больше 0"
        )

    if current_user.balance < balance_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств на балансе"
        )

    current_user.balance -= balance_data.amount
    db.commit()

    # Здесь можно добавить запись в историю операций
    # и отправку уведомления

    return {"message": "Средства успешно списаны", "new_balance": current_user.balance}


@router.get("/history")
async def get_balance_history(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить историю операций с балансом
    (Требуется реализация таблицы balance_transactions)
    """
    # Заглушка для будущей реализации
    return {"message": "История операций будет доступна после реализации"}