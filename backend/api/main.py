from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, books, users, loans, admin
import database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os

# Scheduler for periodic reset
scheduler = AsyncIOScheduler()
reset_interval_hours = int(
    os.getenv("RESET_INTERVAL_HOURS", 24))


@scheduler.scheduled_job(IntervalTrigger(hours=reset_interval_hours))
def scheduled_reset():
    database.reset_db()
    print("Database reset completed.")


# Lifespan function to initialize database and start scheduler on app startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    database.init_db()
    database.seed_db()

    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Library Management API", version="1.0", lifespan=lifespan)


# Add CORS middleware
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Library Management API"}
