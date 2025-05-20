from fastapi import Depends, HTTPException, status
from app.auth import get_current_user
from app.models import User

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
