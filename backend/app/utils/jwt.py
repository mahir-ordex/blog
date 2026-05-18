import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

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

            payload: dict[str, Any] = {
                "id": user.id,
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }
            return jwt.encode(payload, secret, algorithm="HS256")

        except JWTError as e:
            return e
        