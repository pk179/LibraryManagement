from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

import api.schemas as schemas
import api.auth as auth
import users
import logger

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


@router.post("/register", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserRegister):
    """
    Register a new user.
    """
    try:
        ok = users.register_user(
            payload.username, payload.password, payload.role)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")
        return {"message": "User registered"}
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error during register endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin):
    """
    Authenticate user and return JWT token.
    """
    try:
        user = users.authenticate_user(payload.username, payload.password)
        if not user:
            logger.log_warning(
                f"Failed login attempt for username: {payload.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        token_data = {"sub": str(
            user["id"]), "username": user["username"], "role": user["role"]}
        access_token = auth.create_access_token(token_data)

        logger.log_info(f"User '{user['username']}' logged in, token issued.")
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error during login endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
