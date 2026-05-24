from typing import List, Optional

from fastapi import Request, HTTPException
from app.utils.jwt import JWTServices

async def verify_auth(request: Request, required_roles: Optional[List[str]] = None):
    try:
        token = request.cookies.get("token")
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        
        user = getattr(JWTServices, "verift_token")(token)

        if required_roles and user.get("role") not in required_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required role: {required_roles}"
            )
        request.state.user = user
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    
async def require_admin(request: Request):
    await verify_auth(request, required_roles=["admin"])
    return request.state.user

async def require_user(request: Request):
    await verify_auth(request, required_roles=["user"])
    return request.state.user
async def require_both(request: Request):
    await verify_auth(request, required_roles=["user","admin"])
    return request.state.user


