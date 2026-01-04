from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from api.auth import current_user_dep
from api.schemas import (
    BookResponse,
    BookCreate,
    BookUpdate,
    MessageResponse
)
import books
import database
import logger

router = APIRouter(
    prefix="/api/books",
    tags=["Books"],
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


@router.get("/", response_model=list[BookResponse])
def get_all_books(available: bool = False):
    """
    Return all books or only available ones.
    """
    try:
        rows = database.get_all_books(only_available=available)
        return [BookResponse(**b) for b in rows]
    except Exception as e:
        print(f"Error reading books list: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/view/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """
    Get book details by ID.
    """
    try:
        book = database.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return BookResponse(**book)
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error getting book by id: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_book(payload: BookCreate, admin=Depends(admin_required)):
    """
    Add a new book (admin only).
    """
    try:
        book, created = books.add_book(
            payload.title,
            payload.author,
            payload.year,
            payload.quantity,
            payload.genre,
            payload.isbn
        )

        if created:
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=book)
        else:
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=book)
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error adding book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{book_id}", response_model=MessageResponse)
def update_book(book_id: int, payload: BookUpdate, admin=Depends(admin_required)):
    """
    Update book fields by ID (admin only).
    """
    try:
        book = books.update_book(
            book_id,
            payload.title,
            payload.author,
            payload.year,
            payload.quantity,
            payload.genre,
            payload.isbn
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=book)
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error updating book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int, admin=Depends(admin_required)):
    """
    Delete a book by ID (admin only).
    """
    try:
        books.delete_book(book_id)
        return {"message": "Book deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.log_exception(f"Unexpected error deleting book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=list[BookResponse])
def search_books(
    q: str,
    available: bool = False,
    genre: str | None = None
):
    """
    Search books by title, author or genre.
    """
    try:
        results = database.search_books(
            query=q,
            only_available=available,
            genre_filter=genre
        )
        return [BookResponse(**b) for b in results]
    except Exception as e:
        print(f"Error searching books: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
