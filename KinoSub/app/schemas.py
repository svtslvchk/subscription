from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
import uuid

# !!! классы для USER !!!
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    role: str
    balance: float

    class Config:
        from_attributes = True

# !!! классы для SUBSCRIPTOIN !!!
class SubscriptionBase(BaseModel):
    name: str
    price: float
    duration_days: int
    description: Optional[str] = None
    is_active: bool = True
    discount_rate: Optional[float] = None
    discount_until: Optional[date] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    discount_rate: Optional[float] = None
    discount_until: Optional[date] = None

class SubscriptionOut(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True

# !!! классы для USERSUBSCRIPTIONS !!!
from pydantic import BaseModel
from datetime import date

class UserSubscriptionBase(BaseModel):
    user_id: int
    subscription_id: int
    end_date: date
    auto_renew: bool = False

class UserSubscriptionCreate(UserSubscriptionBase):
    pass

class UserSubscriptionOut(UserSubscriptionBase):
    id: int
    start_date: date
    is_active: bool

    class Config:
        from_attributes = True  # Для работы с ORM


# !!! классы для PAYMENT !!!
class PaymentBase(BaseModel):
    user_id: int
    subscription_id: int
    amount: float
    payment_method: str

class PaymentCreate(BaseModel):
    subscription_id: int
    amount: float
    payment_method: str = "balance"


class PaymentOut(PaymentCreate):
    id: int
    status: str
    external_id: str
    created_at: datetime
    is_refunded: bool

    class Config:
        from_attributes = True

class BalanceUpdate(BaseModel):
    amount: float
    description: Optional[str] = None


class NotificationBase(BaseModel):
    user_id: int
    message: str
    type: str  # 'payment', 'refund', 'subscription' и т.д.

class NotificationCreate(NotificationBase):
    is_read: bool = False  # Значение по умолчанию

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationOut(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Ранее называлось orm_mode






