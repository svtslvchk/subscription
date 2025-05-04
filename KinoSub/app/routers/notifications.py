from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Notification, User
from app.schemas import NotificationOut, NotificationUpdate
from app.auth import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/", response_model=List[NotificationOut])
def get_notifications(
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить уведомления пользователя"""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if unread_only:
        query = query.filter(Notification.is_read == False)

    return query.order_by(Notification.created_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_as_read(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Пометить уведомление как прочитанное"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification