from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from app.models.model import User
from app.middleware.auth import require_both, require_user

route = APIRouter(prefix="/users", tags=["users"])


class UpdateUserBody(BaseModel):
    name: str | None = None
    email: str | None = None
    bio: str | None = None
    role: str | None = None


@route.get("/{user_id}")
def get_user_by_id(user_id: int, req: Request, db: Session = Depends(get_db), user: Dict[str, Any] = Depends(require_both)) -> Dict[str, Any]:
    try:
        current_user = req.state.user

        if not current_user:
            raise HTTPException(status_code=403, detail="Unauthorized Request User!")
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "bio": db_user.bio,
            "role": db_user.role,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Messages : {e}")


@route.patch("/")
def update_user(req: Request, payload: UpdateUserBody = Body(...), user: Dict[str, Any] = Depends(require_both), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        current_user = req.state.user

        data = payload.model_dump(exclude_unset=True)

        if not current_user:
            raise HTTPException(status_code=403, detail="Unauthorized Request User!")

        db_user = db.query(User).filter(User.id == current_user["id"]).first()

        if not db_user:
            raise HTTPException(404, "User not found")
        if "email" in data and data["email"] != db_user.email:
            if db.query(User).filter(User.email == data["email"]).first():
                raise HTTPException(400, "Email already in use")

        if "role" in data and current_user.get("role") != "admin":
            raise HTTPException(403, "Cannot change role")
        for k, v in data.items():
            setattr(db_user, k, v)

        db.commit()
        db.refresh(db_user)

        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "bio": db_user.bio,
            "role": db_user.role,
        }

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"Error {e}")


@route.delete("/")
def delete_user(req: Request, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)) -> JSONResponse:
    try:
        if not current_user:
            raise HTTPException(status_code=403, detail="Unauthorized User!")

        db.query(User).filter(User.id == current_user["id"]).delete(synchronize_session=False)
        db.commit()

        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@route.patch("/{user_id}")
def update_user_by_id(user_id:int,req:Request,payload:UpdateUserBody=Body(...),db:Session=Depends(get_db)) -> Dict[str, Any]:
    try:
        current_user = req.state.user
        if not current_user:
            raise HTTPException(status_code=403,detail="Unathorize Request")
        if "admin" is not str(current_user.role):
            raise HTTPException(status_code=403,detail=str("Only Admin!"))
        
        data = payload.model_dump(exclude_unset=True)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404,detail="User Not Found!")
        
        for k,v in data.items():
            setattr(user,k,v)
        db.commit()
        db.refresh(user)

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "bio": user.bio,
            "role": user.role,
        } 
    except HTTPException as e:
        raise HTTPException(status_code=400,detail=str(e))
