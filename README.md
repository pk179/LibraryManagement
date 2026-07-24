# Library Management System

A full-stack Library Management System built with **FastAPI (Python)** and **React + TypeScript**.

The database is automatically seeded on the first run with demo data and resets every 24 hours using APScheduler to keep the application in a consistent state.

## Live Demo

The application is available here:

https://librarymanagement-frontend-944m.onrender.com/

## Features

### User

* Register and log in
* Browse and search books
* Borrow and return books
* View active, overdue and returned loans

### Admin

* Manage books (CRUD)
* Manage users
* View system statistics
* Monitor all loans
* Reset the demo database

## Demo accounts

These accounts are available in the live demo.

### Admin account

```
Username: admin
Password: Admin123
```

### User account

```
Username: user
Password: User12345
```

## Tech Stack

### Backend

* FastAPI
* Pydantic
* SQLite
* JWT Authentication
* bcrypt
* APScheduler

### Frontend

* React 19
* TypeScript
* Vite
* Axios

### Testing

* Postman (API testing)
* Pytest (API & integration testing)
* Playwright (End-to-End testing)

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 20.19+
* npm 9+

### Backend

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate

cd backend

pip install -r requirements.txt

uvicorn api.main:app --reload
```

Swagger documentation:

```
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

Application:

```
http://localhost:5173
```

## Automated Tests

The project includes automated tests covering the backend API and end-to-end frontend user workflows.

### Backend

* 50+ Pytest test cases
* API and integration testing
* Negative scenarios
* Boundary value testing
* Edge cases

Run:

```bash
cd backend
pytest -v
```

### Frontend

* Playwright end-to-end test suites
* User and admin workflows

Run:

```bash
cd frontend
npx playwright test
```
