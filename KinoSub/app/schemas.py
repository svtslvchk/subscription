from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional

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




