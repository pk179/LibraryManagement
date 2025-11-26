# api/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

import database as db
import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.isoformat(), "iat": now.isoformat()})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.log_info(f"Created access token for subject={data.get('sub')}")
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.log_warning(f"JWT decode failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication token")


def get_current_user_dep(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    sub = payload.get("sub")
    if sub is None:
        logger.log_warning("Token missing subject (sub)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    exp_iso = payload.get("exp")
    if exp_iso:
        try:
            exp_dt = datetime.fromisoformat(exp_iso)
            if exp_dt < datetime.now(timezone.utc):
                logger.log_warning(f"Token expired for sub={sub}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except Exception:
            logger.log_warning("Token 'exp' parse failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token expiry")

    # Get user from DB
    user_row = db.get_user_by_id(sub)
    if not user_row:
        logger.log_warning(f"Token valid but user not found: id={sub}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_id, username, _hashed_pw, role = user_row
    logger.log_info(
        f"Authenticated request as user id={user_id}, username={username}")
    return {"id": user_id, "username": username, "role": role}


current_user_dep = get_current_user_dep
