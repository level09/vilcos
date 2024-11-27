from typing import Optional, Callable
from fastapi import Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from vilcos.models import User
from vilcos.schemas import UserSchema
from vilcos.db import get_db
from functools import wraps

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """Get the current user from session."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
        
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            request.session.clear()
        return user
    except Exception:
        request.session.clear()
        return None

def auth_required(redirect_to_signin: bool = True):
    """Protect routes with authentication."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            db = kwargs.get('db')
            
            if not request or not db:
                raise HTTPException(
                    status_code=500,
                    detail="Request or DB session not found"
                )
            
            user = await get_current_user(request, db)
            if not user:
                if redirect_to_signin:
                    return RedirectResponse(
                        url="/auth/signin",
                        status_code=status.HTTP_303_SEE_OTHER
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            kwargs['user'] = UserSchema.from_orm(user)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def login_user(request: Request, user: User) -> None:
    """Log in a user by setting their ID in the session."""
    request.session["user_id"] = user.id

def logout_user(request: Request) -> None:
    """Log out a user by clearing their session."""
    request.session.clear()
