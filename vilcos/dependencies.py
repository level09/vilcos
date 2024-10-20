# vilcos/dependencies.py
from fastapi import Request, HTTPException

def login_required(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

