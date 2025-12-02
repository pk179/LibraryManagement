from fastapi import APIRouter, Depends, HTTPException, status
from api.auth import current_user_dep
from api.schemas import UserResponse
import database

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
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


@router.get("/", response_model=list[UserResponse])
def list_users(admin=Depends(admin_required)):
    """
    List all users. Admin access required.
    """
    try:
        users = database.get_all_users()
        return [UserResponse(**u) for u in users]
    except Exception as e:
        print(f"Error reading user list: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.delete("/{user_id}")
def delete_user(user_id: int, admin=Depends(admin_required)):
    """
    Delete a user by ID. Admin access required.
    """
    try:
        user = database.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user["id"] == admin["id"]:
            raise HTTPException(
                status_code=400, detail="Admin cannot delete themselves")

        database.delete_user(user_id)
        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
