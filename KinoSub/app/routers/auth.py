from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from jose import jwt
from datetime import timedelta, datetime
from app.auth import get_current_user
from app.schemas import UserOut
from app.models import User

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



@router.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.username == form_data.username).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Проверка пароля
        if not pwd_context.verify(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        import traceback
        traceback.print_exc()  # Распечатает в консоль
        raise HTTPException(status_code=500, detail=str(e))  # Вернёт точную ошибку в ответ

@router.get("/me", tags=["auth"])
@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user