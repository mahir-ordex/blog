import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class JWTServices:
    @staticmethod
    def verift_token(token: str):
        try:
            secret: Optional[str] = os.getenv("JWT_SECRET")
            if secret is None:
                raise ValueError("JWT_SECRET is not set")
            user = jwt.decode(token, secret, algorithms=["HS256"])

            return user
        except JWTError as e:
            return e
    @staticmethod
    def generate_token(user: Any):
        try:
            secret: Optional[str] = os.getenv("JWT_SECRET")
            if secret is None:
                raise ValueError("JWT_SECRET is not set")
            exp_env = os.getenv("JWT_EXP")
            if exp_env is None:
                raise ValueError("JWT_EXP is not set")
            try:
                exp_hours = float(exp_env)
            except ValueError:
                raise ValueError("JWT_EXP must be a number")

            payload: dict[str, Any] = {
                "id": user.id,
                "email": user.email,
                "role":user.role,
                "exp": datetime.now(timezone.utc) + timedelta(hours=exp_hours),
            }
            return jwt.encode(payload, secret, algorithm="HS256")

        except JWTError as e:
            return e
        