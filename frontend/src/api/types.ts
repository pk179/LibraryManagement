export interface UserRegister {
    username: string;
    password: string;
    role?: string;
}

export interface UserLogin {
    username: string;
    password: string;
}

export interface UserResponse {
    id: number;
    username: string;
    role: string;
}

export interface RegisterResponse {
    message: string;
    user: UserResponse;
}

export interface BookCreate {
    title: string;
    author: string;
    year: number;
    quantity: number;
    genre?: string;
    isbn?: string;
}

export interface BookUpdate {
    title?: string;
    author?: string;
    year?: number;
    quantity?: number;
    genre?: string;
    isbn?: string;
}

export interface BookResponse {
    id: number;
    title: string;
    author: string;
    year: number;
    quantity: number;
    genre?: string;
    isbn?: string;
}

export interface PostBookResponse {
    message: string;
    book: BookResponse;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface MessageResponse {
    message: string;
}

export interface LoanCreate {
    book_id: number;
}

export interface LoanReturn {
    book_id: number;
}

export interface LoanResponse {
    id: number;
    user_id: number;
    book_id: number;
    borrow_date: string;
    due_date: string;
    return_date: string | null;
    fine: number;
}

export interface LoanActionResponse {
    message: string;
    loan: LoanResponse;
}

export interface LoanStatsResponse {
    total: number;
    active: number;
    overdue: number;
    returned: number;
}

export interface BulkDeleteResponse {
    deleted: number[];
    not_found: number[];
}