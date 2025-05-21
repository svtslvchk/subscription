from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date
from sqlalchemy import Enum as PgEnum
import enum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), default="user", nullable=False)
    balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscriptions = relationship("UserSubscription", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    discount_rate = Column(Numeric(3, 2), nullable=True)
    discount_until = Column(Date, nullable=True)

    users = relationship("UserSubscription", back_populates="subscription")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    start_date = Column(Date, default=date.today())  # Дата начала подписки
    end_date = Column(Date)                         # Дата окончания
    is_active = Column(Boolean, default=True)       # Активна ли подписка
    auto_renew = Column(Boolean, default=False)     # Автопродление

    # Связи с таблицами (опционально, для удобства)
    user = relationship("User", back_populates="subscriptions")
    subscription = relationship("Subscription", back_populates="users")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Numeric(10, 2))
    status = Column(String(20))
    payment_method = Column(String(20))
    external_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_refunded = Column(Boolean, default=False)
    refund_reason = Column(Text, nullable=True)



class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")



class TransactionType(enum.Enum):
    topup = "topup"
    withdraw = "withdraw"

class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(PgEnum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class SubscriptionRequest(Base):
    __tablename__ = "subscription_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    status = Column(String, default="pending")  # pending / approved / rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    subscription = relationship("Subscription")


