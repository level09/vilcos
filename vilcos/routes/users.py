from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from vilcos.models import User, Role
from vilcos.db import get_db
from vilcos.auth_utils import get_current_user
from vilcos.utils import get_root_path
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))

@router.get("/admin/users")
async def users_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Render the users management page."""
    if not current_user:
        return RedirectResponse(url="/auth/signin", status_code=303)
        
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": current_user}
    )

@router.get("/api/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users with their roles."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return {
        "items": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "roles": [{"id": role.id, "name": role.name} for role in user.roles],
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    }

@router.get("/api/roles")
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available roles."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return {"items": [{"id": role.id, "name": role.name} for role in roles]}

@router.post("/api/users")
async def create_user(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Validate required fields
        if not all(key in data for key in ["email", "username", "password"]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Check if email or username exists
        if await User.email_exists(db, data["email"]):
            raise HTTPException(status_code=400, detail="Email already exists")
        if await User.username_exists(db, data["username"]):
            raise HTTPException(status_code=400, detail="Username already exists")

        # Get roles by IDs
        role_ids = [r["id"] if isinstance(r, dict) else r for r in data.get("roles", [])]
        result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
        roles = result.scalars().all()
        
        if len(roles) != len(role_ids):
            raise HTTPException(status_code=400, detail="One or more invalid role IDs")
        
        # Create user with roles
        user = User(
            email=data["email"],
            username=data["username"],
            password=User.get_password_hash(data["password"]),
            roles=roles,
            is_active=data.get("is_active", True)
        )
        db.add(user)
        await db.commit()
        
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "roles": [{"id": role.id, "name": role.name} for role in user.roles]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/api/users/{user_id}")
async def update_user(
    user_id: int,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing user."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        user = await User.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if email or username already exists for another user
        if data.get("email") and await User.email_exists(db, data["email"], exclude_id=user_id):
            raise HTTPException(status_code=400, detail="Email already exists")
        if data.get("username") and await User.username_exists(db, data["username"], exclude_id=user_id):
            raise HTTPException(status_code=400, detail="Username already exists")

        # Update basic fields
        if data.get("email"):
            user.email = data["email"]
        if data.get("username"):
            user.username = data["username"]
        if data.get("password"):
            user.password = User.get_password_hash(data["password"])
        if "is_active" in data:
            user.is_active = data["is_active"]

        # Update roles if provided
        if "roles" in data:
            role_ids = [r["id"] if isinstance(r, dict) else r for r in data["roles"]]
            result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
            roles = result.scalars().all()
            
            if len(roles) != len(role_ids):
                raise HTTPException(status_code=400, detail="One or more invalid role IDs")
                
            user.roles = roles

        await db.commit()
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "roles": [{"id": role.id, "name": role.name} for role in user.roles]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        user = await User.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent deleting the last admin user
        if user.is_admin and await User.get_admin_count(db) <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the last admin user"
            )

        await db.delete(user)
        await db.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
