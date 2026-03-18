from fastapi import APIRouter, Depends, HTTPException, status
from api.auth import current_user_dep
import database

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


def admin_required(current_user=Depends(current_user_dep)):
    """
    Dependency to ensure the current user is an admin.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_database(admin=Depends(admin_required)):
    database.reset_db()
    return {"message": "Database reset successfully"}
