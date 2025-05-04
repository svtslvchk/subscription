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

@router.post("/", response_model=UserSubscriptionOut, status_code=status.HTTP_201_CREATED)
def assign_subscription(
    subscription: UserSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Назначение подписки пользователю с валидацией:
    - Проверка существования пользователя и подписки
    - Проверка активных подписок пользователя
    - Валидация даты окончания
    - Автоматический расчёт end_date при необходимости
    """
    # Проверяем существование пользователя и подписки
    db_user = db.query(User).get(subscription.user_id)
    db_sub = db.query(Subscription).get(subscription.subscription_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if not db_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    # Проверяем активные подписки пользователя
    active_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == subscription.user_id,
        UserSubscription.is_active == True,
        UserSubscription.end_date >= date.today()
    ).first()

    if active_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У пользователя уже есть активная подписка"
        )

    # Валидация даты окончания
    if subscription.end_date:
        if subscription.end_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата окончания не может быть в прошлом"
            )
        end_date = subscription.end_date
    else:
        end_date = date.today() + timedelta(days=db_sub.duration_days)

    # Создаем запись о подписке
    db_user_sub = UserSubscription(
        user_id=subscription.user_id,
        subscription_id=subscription.subscription_id,
        start_date=date.today(),
        end_date=end_date,
        is_active=True,
        auto_renew=subscription.auto_renew
    )

    try:
        db.add(db_user_sub)
        db.commit()
        db.refresh(db_user_sub)
        return db_user_sub
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании подписки: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[UserSubscriptionOut])
def get_user_subscriptions(
    user_id: int,
    db: Session = Depends(get_db)
):

    subscriptions = db.query(UserSubscription)\
        .filter(UserSubscription.user_id == user_id)\
        .all()
    for sub in subscriptions:
        if sub.end_date < date.today():
            sub.is_active = False
    db.commit()
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