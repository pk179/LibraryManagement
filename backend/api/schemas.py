from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str]


class UserLogin(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "jan_kowalski"})
    password: str = Field(..., json_schema_extra={"example": "haslo123"})


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class BookCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Wiedźmin"})
    author: str = Field(..., json_schema_extra={
                        "example": "Andrzej Sapkowski"})
    year: int = Field(..., json_schema_extra={"example": 1993})
    quantity: int = Field(default=1, json_schema_extra={"example": 3})
    genre: Optional[str] = Field(
        default="", json_schema_extra={"example": "fantasy"})
    isbn: Optional[str] = Field(default=None, json_schema_extra={
                                "example": "9788375780635"})


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

    model_config = ConfigDict(from_attributes=True)


class PostBookResponse(BaseModel):
    message: str
    book: BookResponse


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
    title: str
    author: str
    borrow_date: str
    due_date: str
    return_date: str | None
    fine: float


class LoanActionResponse(BaseModel):
    message: str
    loan: LoanResponse


class LoanStatsResponse(BaseModel):
    total_loans: int
    active_loans: int
    overdue_loans: int
    returned_loans: int


class BulkDeleteResponse(BaseModel):
    deleted: List[int]
    not_found: List[int]
