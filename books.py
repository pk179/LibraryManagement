from fastapi import HTTPException, status
import validation as v
import database as db
import logger


def add_book(title, author, year, quantity=1, genre=None, isbn=None):
    """
    Add a new book or increase quantity if ISBN already exists.
    """
    try:
        v.validate_book_data(title, author, year, quantity, genre, isbn)
        normalized_isbn = v.normalize_isbn(isbn)

        # Check if ISBN already exists, if it does, increase quantity
        if normalized_isbn:
            all_books = db.get_all_books()
            for book in all_books:
                if book["isbn"] == normalized_isbn:
                    db.update_book_row(
                        book["id"],
                        quantity=book["quantity"] + int(quantity)
                    )
                    logger.log_info(
                        f"Updated quantity for ISBN={normalized_isbn} by {quantity}"
                    )
                    return

        # Insert new book entry
        book = db.add_book_row(
            title=title,
            author=author,
            year=year,
            quantity=quantity,
            genre=genre or "",
            isbn=normalized_isbn or None
        )

        if not book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book with this ISBN already exists"
            )

        logger.log_info(f"New book added: {title} ({year})")

    except ValueError as e:
        logger.log_warning(f"Validation error while adding book: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.log_exception(f"Unexpected error in add_book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def update_book(book_id, title=None, author=None, year=None, quantity=None, genre=None, isbn=None):
    """
    Update the book with the given ID.
    You can change the title, author, year, quantity, genre and ISBN.
    """
    try:
        if not db.book_exists(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        updates = {}

        if title is not None:
            v.validate_non_empty_string("Title", title)
            updates["title"] = title

        if author is not None:
            v.validate_non_empty_string("Author", author)
            updates["author"] = author

        if year is not None:
            v.validate_year(year)
            updates["year"] = year

        if quantity is not None:
            v.validate_quantity(quantity)
            updates["quantity"] = quantity

        if genre is not None:
            v.validate_genre(genre)
            updates["genre"] = genre

        if isbn is not None:
            v.validate_isbn_optional(isbn)
            updates["isbn"] = v.normalize_isbn(isbn)

        if not updates:
            return

        updated = db.update_book_row(book_id, **updates)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed"
            )

        logger.log_info(f"Book updated: ID={book_id}")

    except ValueError as e:
        logger.log_warning(f"Validation error while updating book: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.log_exception(f"Unexpected error in update_book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def delete_book(book_id):
    """
    Delete a book by ID.
    """
    try:
        if not db.book_exists(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        success = db.delete_book(book_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delete failed"
            )

        logger.log_info(f"Book deleted: ID={book_id}")

    except HTTPException:
        raise

    except Exception as e:
        logger.log_exception(f"Unexpected error in delete_book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
