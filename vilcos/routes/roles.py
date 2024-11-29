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

@router.get("/admin/roles")
async def roles_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Render the roles management page."""
    if not current_user:
        return RedirectResponse(url="/auth/signin", status_code=303)
        
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    return templates.TemplateResponse(
        "admin/roles.html",
        {"request": request, "user": current_user}
    )

@router.get("/api/roles")
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    
    return {
        "items": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "created_at": role.created_at.isoformat() if role.created_at else None
            }
            for role in roles
        ]
    }

@router.post("/api/roles")
async def create_role(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Validate required fields
        if "name" not in data:
            raise HTTPException(status_code=400, detail="Role name is required")

        # Check if role name exists
        result = await db.execute(select(Role).where(Role.name == data["name"]))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Role name already exists")

        # Create role
        role = Role(
            name=data["name"],
            description=data.get("description", "")
        )
        db.add(role)
        await db.commit()
        
        return {
            "status": "success",
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/api/roles/{role_id}")
async def update_role(
    role_id: int,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing role."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Get the role
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Check if name exists for another role
        if data.get("name") and data["name"] != role.name:
            result = await db.execute(
                select(Role).where(
                    Role.name == data["name"],
                    Role.id != role_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Role name already exists")

        # Update fields
        if "name" in data:
            role.name = data["name"]
        if "description" in data:
            role.description = data["description"]

        await db.commit()
        
        return {
            "status": "success",
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a role."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Get the role
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Check if role is in use
        if role.users:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete role that is assigned to users"
            )

        await db.delete(role)
        await db.commit()
        
        return {"status": "success", "message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
