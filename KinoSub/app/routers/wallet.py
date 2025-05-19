from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, BalanceTransaction
from app.schemas import BalanceUpdate
from app.auth import get_current_user
from datetime import datetime
from fastapi import Request
import traceback

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
    return float(current_user.balance)


from decimal import Decimal

@router.post("/topup", status_code=status.HTTP_200_OK)
async def top_up_balance(
    balance_data: BalanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if balance_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сумма пополнения должна быть больше 0"
            )

        amount_decimal = Decimal(str(balance_data.amount))  # 🔥 безопасное преобразование
        current_user.balance += amount_decimal

        transaction = BalanceTransaction(
            user_id=current_user.id,
            amount=amount_decimal,
            type="topup",
            description=balance_data.description or "Пополнение баланса"
        )

        db.add(transaction)
        db.commit()
        db.refresh(current_user)

        return {
            "message": "Баланс успешно пополнен",
            "new_balance": float(current_user.balance)
        }

    except Exception as e:
        print("❌ Ошибка при пополнении баланса:")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при пополнении баланса")




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

    transaction = BalanceTransaction(
        user_id=current_user.id,
        amount=balance_data.amount,
        type="withdraw",
        description=balance_data.description or "Списание средств",
        created_at=datetime.utcnow()
    )

    db.add(transaction)
    db.commit()

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
    history = db.query(BalanceTransaction).filter(
        BalanceTransaction.user_id == current_user.id
    ).order_by(BalanceTransaction.created_at.desc()).all()

    return [
        {
            "id": t.id,
            "amount": float(t.amount),
            "type": t.type,
            "description": t.description,
            "created_at": t.created_at.isoformat()
        } for t in history
    ]
