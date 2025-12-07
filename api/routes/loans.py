from fastapi import APIRouter, Depends, HTTPException, status
from api.auth import current_user_dep
from api.schemas import (
    LoanCreate,
    LoanReturn,
    LoanResponse,
    MessageResponse
)
import loans
import database
import logger

router = APIRouter(
    prefix="/api/loans",
    tags=["Loans"],
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


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(payload: LoanCreate, current_user=Depends(current_user_dep)):
    """
    Borrow a book.
    """
    try:
        loans.borrow_book(current_user["id"], payload.book_id)
        return {"message": "Book borrowed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error when borrowing book: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.post("/return", response_model=MessageResponse)
def return_book(payload: LoanReturn, current_user=Depends(current_user_dep)):
    """
    Return a borrowed book.
    """
    try:
        loans.return_book(current_user["id"], payload.book_id)
        return {"message": "Book returned"}
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error when returning book: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/me", response_model=list[LoanResponse])
def get_my_loans(current_user=Depends(current_user_dep)):
    """
    Get active loans of the current user.
    """
    try:
        rows = database.get_loans_by_user(current_user["id"])
        return [LoanResponse(**loan) for loan in rows]
    except Exception as e:
        logger.log_exception(
            f"Unexpected error reading user's active loans: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/returned", response_model=list[LoanResponse])
def get_my_returned(current_user=Depends(current_user_dep)):
    """
    Get the user's returned books (loan history).
    """
    try:
        rows = database.get_returned_loans_by_user(current_user["id"])
        return [LoanResponse(**loan) for loan in rows]
    except Exception as e:
        logger.log_exception(
            f"Unexpected error reading user's returned loans: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/overdue", response_model=list[LoanResponse])
def get_my_overdue(current_user=Depends(current_user_dep)):
    """
    Get overdue loans of the current user (not yet returned and past due date).
    """
    try:
        rows = database.get_overdue_loans_by_user(current_user["id"])
        return [LoanResponse(**loan) for loan in rows]
    except Exception as e:
        logger.log_exception(
            f"Unexpected error reading user's overdue loans: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/active", response_model=list[LoanResponse])
def get_my_active_loans(current_user=Depends(current_user_dep)):
    """
    Get currently borrowed books (not returned).
    """
    try:
        rows = database.get_loans_by_user(current_user["id"])
        return [LoanResponse(**loan) for loan in rows]
    except Exception as e:
        logger.log_exception(
            f"Unexpected error reading user's active loans: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/", response_model=list[LoanResponse])
def get_all_loans(admin=Depends(admin_required)):
    """
    Get all loans (admin only).
    """
    try:
        rows = database.get_all_loans()
        return [LoanResponse(**loan) for loan in rows]
    except Exception as e:
        logger.log_exception(f"Unexpected error when reading all loans: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


@router.get("/stats", response_model=dict)
def loan_stats(admin=Depends(admin_required)):
    """
    Simple loan statistics.
    """
    try:
        total = database.count_all_loans()
        active = database.count_active_loans()
        returned = database.count_returned_loans()

        return {
            "total": total,
            "active": active,
            "returned": returned,
        }
    except Exception as e:
        logger.log_exception(f"Unexpected error reading loan stats: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )
