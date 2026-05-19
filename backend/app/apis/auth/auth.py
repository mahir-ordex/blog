from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import bcrypt
from models.model import User
from db import get_db
from backend.app.utils.jwt import JWTServices

router = APIRouter()


class LoginBody(BaseModel):
    email: str | None = None
    password: str | None = None

class SignupBody(BaseModel):
    name: str | None = None
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
async def signup(body: SignupBody = Body(...), db: Session = Depends(get_db)):
    try:
        email = body.email
        password = body.password
        name = body.name

        if not email:
            raise HTTPException(status_code=400, detail="enter valid email")
        if not password:
            raise HTTPException(status_code=400, detail="enter valid password")
        if not name:
            raise HTTPException(status_code=400, detail="enter valid name")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash the password
        hashPass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        # Create new user
        user = User(name=name, email=email, password=hashPass.decode("utf-8"))
        
        # Save to database
        db.add(user)
        db.commit()
        db.refresh(user)

        token = JWTServices.generate_token(user)
        
        response = JSONResponse(
            status_code=201,
            content={"message": "User created successfully", "data": {"id": str(user.id), "email": user.email}},
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
        raise HTTPException(status_code=400, detail=f"Error Message : {e}")
    
