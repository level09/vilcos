from typing import Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from vilcos.models import User
from vilcos.db import AsyncSessionLocal, get_db

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """
    Get the current user from session.
    
    Args:
        request: FastAPI request object
        db: Database session dependency
        
    Returns:
        Optional[User]: The current user or None if not authenticated
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
        
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            # Clear invalid session
            request.session.clear()
        return user
    except Exception:
        request.session.clear()
        return None

async def get_current_user_or_401(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """
    Get the current user from session, raising 401 if not authenticated.
    
    Args:
        request: FastAPI request object
        db: Database session dependency
        
    Returns:
        User: The current authenticated user
        
    Raises:
        HTTPException: 401 if user is not authenticated
    """
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Session"}
        )
    return user

def login_required(request: Request) -> int:
    """
    Dependency to check if user is authenticated.
    
    Args:
        request: FastAPI request object
        
    Returns:
        int: The user ID if authenticated
        
    Raises:
        HTTPException: 401 if user is not authenticated
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Session"}
        )
    return user_id

def login_user(request: Request, user: User) -> None:
    """
    Log in a user by setting their ID in the session.
    
    Args:
        request: FastAPI request object
        user: User model instance to log in
    """
    request.session["user_id"] = user.id
    request.session["is_authenticated"] = True

def logout_user(request: Request) -> None:
    """
    Log out a user by clearing their session.
    
    Args:
        request: FastAPI request object
    """
    request.session.clear()
