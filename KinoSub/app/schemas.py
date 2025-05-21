from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
import uuid
from enum import Enum
from decimal import Decimal

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
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PaymentCreate(BaseModel):
    subscription_id: int
    amount: Decimal
    payment_method: str  # "balance", "card", "yoomoney" и т.д.


class PaymentOut(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    amount: Decimal
    status: str
    payment_method: str
    external_id: Optional[str]
    created_at: datetime
    is_refunded: Optional[bool]
    refund_reason: Optional[str]

    class Config:
        orm_mode = True


class RefundRequest(BaseModel):
    reason: Optional[str] = "No reason provided"



from decimal import Decimal

class BalanceUpdate(BaseModel):
    amount: Decimal
    description: Optional[str] = None




class NotificationBase(BaseModel):
    user_id: int
    message: str
    type: str  # 'payment', 'refund', 'subscription' и т.д.

class NotificationCreate(NotificationBase):
    is_read: bool = False  # Значение по умолчанию

class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str



class TransactionType(str, Enum):
    topup = "topup"
    withdraw = "withdraw"

class BalanceTransactionOut(BaseModel):
    id: int
    amount: float
    type: TransactionType
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True



class SubscriptionRequestCreate(BaseModel):
    subscription_id: int

class SubscriptionRequestOut(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True












