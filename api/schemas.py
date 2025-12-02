from pydantic import BaseModel, Field
from typing import Optional


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30,
                          example="jan_kowalski")
    password: str = Field(..., min_length=8, example="haslo123")
    role: Optional[str] = Field(default="user", example="user")


class UserLogin(BaseModel):
    username: str = Field(..., example="jan_kowalski")
    password: str = Field(..., example="haslo123")


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True


class BookCreate(BaseModel):
    title: str = Field(..., example="Wiedźmin: Ostatnie życzenie")
    author: str = Field(..., example="Andrzej Sapkowski")
    year: int = Field(..., example=1993)
    quantity: int = Field(default=1, example=3)
    genre: Optional[str] = Field(default="", example="fantasy")
    isbn: Optional[str] = Field(default=None, example="9788375780635")


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    quantity: Optional[int] = None
    genre: Optional[str] = None
    isbn: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    quantity: int
    genre: Optional[str]
    isbn: Optional[str]

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


class LoanCreate(BaseModel):
    book_id: int


class LoanReturn(BaseModel):
    book_id: int


class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: str
    due_date: str
    return_date: str | None
    fine: float
