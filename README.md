# PayFlow API

A banking-style REST API built with **FastAPI** and **async SQLAlchemy**, featuring JWT authentication, account management, and money transfers — built as a hands-on project to learn production-grade backend development, from the ground up, one concept at a time.

## Features

- **User authentication** — registration with Argon2 password hashing, JWT-based login, and protected routes using FastAPI's dependency injection
- **Account management** — open bank accounts linked to authenticated users via a one-to-many relationship
- **Money movement** — deposit, withdraw, and transfer between accounts, with strict ownership checks and balance validation
- **Data integrity** — money stored as exact `Decimal` values (never floating-point), enforced foreign keys, and atomic transactions for transfers
- **Automated testing** — a `pytest` suite covering registration, deposits, withdrawals, transfers, and cross-user authorization boundaries, run against an isolated test database

## Tech Stack

- **Framework:** FastAPI
- **Database / ORM:** SQLAlchemy (async) with SQLite
- **Validation:** Pydantic
- **Authentication:** JWT (PyJWT) + Argon2 password hashing (pwdlib)
- **Testing:** pytest + httpx
- **Package management:** uv

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Create a new user account |
| POST | `/login` | Authenticate and receive a JWT access token |
| GET | `/me` | Get the current authenticated user's details |
| POST | `/accounts` | Open a new bank account for the current user |
| GET | `/accounts/{account_id}` | View an account's balance and status |
| POST | `/accounts/{account_id}/deposit` | Deposit funds into an account |
| POST | `/accounts/{account_id}/withdraw` | Withdraw funds from an account |
| POST | `/accounts/{account_id}/transfer` | Transfer funds to another account |

Full interactive documentation is available at `/docs` once the server is running.

## Getting Started

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
# Clone the repository
git clone https://github.com/AntonSinthu/PayflowAPI.git
cd PayflowAPI

# Install dependencies (handled automatically by uv on first run)
uv sync

# Create a .env file with the following variables:
# DATABASE_URL=sqlite+aiosqlite:///./payflow.db
# SECRET_KEY=<generate with: uv run python -c "import secrets; print(secrets.token_hex(32))">
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=60

# Run the development server
uv run fastapi dev app/main.py
```

Visit `http://127.0.0.1:8000/docs` to explore the API interactively.

## Running Tests

```bash
uv run pytest -v
```

Tests run against a completely isolated, throwaway database — never the development database — and cover authentication, account operations, and security boundaries (e.g. verifying users cannot access or modify accounts they don't own).

## Roadmap

Planned additions, building toward a more production-ready setup:

- [ ] PostgreSQL support (replacing SQLite)
- [ ] Docker & Docker Compose for containerized local development
- [ ] Alembic for versioned database migrations
- [ ] Refresh tokens
- [ ] Account freezing / status management
- [ ] Pagination on list endpoints

## Why This Project

PayFlow was built to develop a genuine, from-first-principles understanding of backend engineering — not just following a tutorial, but understanding *why* each design decision was made: why dependency injection is used for database sessions, why passwords are hashed rather than encrypted, why money is stored as `Decimal` rather than `float`, why foreign keys sit on the "many" side of a relationship, and why every write to two accounts during a transfer happens inside a single atomic transaction.

## License

This project is for educational and portfolio purposes.
