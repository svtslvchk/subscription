from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/promote/{user_id}")
def promote_to_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    db.commit()
    return {"message": f"User {user_id} promoted to admin"}
