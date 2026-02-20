from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, books, users, loans
import database

app = FastAPI(title="Library Management API", version="1.0")

# Initialize database
database.init_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)


@app.get("/")
def root():
    return {"message": "Library Management API"}
