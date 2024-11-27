from fastapi import Request, HTTPException
from sqlalchemy import select
from vilcos.models import User
from vilcos.db import AsyncSessionMaker

async def get_current_user(request: Request):
    """Get the current user from session."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
        
    async with AsyncSessionMaker() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user

def login_required(request: Request):
    """Dependency to check if user is authenticated."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

def login_user(request: Request, user: User):
    """Log in a user by setting their ID in the session."""
    request.session["user_id"] = user.id
    request.session["is_authenticated"] = True

def logout_user(request: Request):
    """Log out a user by clearing their session."""
    request.session.clear()
