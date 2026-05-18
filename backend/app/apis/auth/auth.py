from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from gotrue import Session
from pydantic import BaseModel
import bcrypt
from models.model import User
from db import get_db
from backend.app.utils.jwt import JWTServices

router = APIRouter()


class LoginBody(BaseModel):
    email: str | None = None
    password: str | None = None

@router.post("/login")
async def login(body: LoginBody = Body(...), db = Depends(get_db)):
    try:
        email = body.email
        password = body.password

        if not email:
            raise HTTPException(status_code=400,detail="enter valid email")
        if not password:
            raise HTTPException(status_code=400,detail="enter valid password")
        
        hashPass = db.query(User).filter(User.email == email).first()

        if not hashPass:
            raise HTTPException(status_code=400, detail="User not found")
        
        stored_password: str = str(hashPass.password)
        isAuth = bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))

        if not isAuth:
            raise HTTPException(status_code=400,detail="Wrong Password!")

        token = JWTServices.generate_token(hashPass)

        if not token:
            raise HTTPException(status_code=400,detail="Error in Generating Token!")
        
        response = JSONResponse(
            status_code=200,
            content={"message": "login successful", "data": {"id": str(hashPass.id),"email":hashPass.email}},
        )
        response.set_cookie(
            key="token",
            value=str(token),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60,
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Error Message : {e}")

@router.post("/signup")
async def signup(body=Body(...),db:Session=Depends(get_db)):
    
