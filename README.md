# StoreOps API

![CI](https://github.com/Punchdevlider/storeops-api/actions/workflows/ci.yml/badge.svg)

StoreOps API is a REST API for managing a small e-commerce back office:
categories, products, customers, orders, stock levels, and order status history.

It is built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**,
**Docker Compose**, and **pytest**.


## Highlights

* Layered architecture: `routers` (HTTP) в†’ `services` (business logic) в†’ `models` (ORM).
* Fully typed SQLAlchemy 2.0 models using `Mapped[...]` and `mapped_column`.
* Pydantic v2 schemas for request validation and response serialization.
* Atomic order creation: stock is validated and decremented inside a single
  transaction, with a row-level lock (`SELECT ... FOR UPDATE`) to prevent
  overselling under concurrent requests.
* Monetary values stored and computed with `Decimal`, never `float`.
* Integration tests run against an isolated in-memory SQLite database, so the
  suite needs no running PostgreSQL instance.
* GitHub Actions CI runs the linter (ruff) and the test suite on every push.

## Tech Stack

Python 3.12 В· FastAPI В· PostgreSQL В· SQLAlchemy 2.0 В· Alembic В· Docker В·
Docker Compose В· pytest В· ruff

## Architecture

```text
HTTP request
    в”‚
    в–ј
routers/        validate input, map domain errors to HTTP status codes
    в”‚
    в–ј
services/       business logic, transactions, stock locking
    в”‚
    в–ј
models/         SQLAlchemy ORM entities
    в”‚
    в–ј
PostgreSQL
```

Request and response bodies are defined in `schemas/` (Pydantic). The database
session is provided per-request via the `get_db` dependency, which rolls back
on failure and always closes the session.

## Project Structure

```text
storeops-api/
в”њв”Ђв”Ђ app/
в”‚   в”њв”Ђв”Ђ main.py          # FastAPI app, root and health endpoints
в”‚   в”њв”Ђв”Ђ config.py        # Settings loaded from environment / .env
в”‚   в”њв”Ђв”Ђ database.py      # Engine, session factory, get_db dependency
в”‚   в”њв”Ђв”Ђ models/          # SQLAlchemy ORM models
в”‚   в”њв”Ђв”Ђ schemas/         # Pydantic request/response models
в”‚   в”њв”Ђв”Ђ routers/         # API endpoints
в”‚   в””в”Ђв”Ђ services/        # Business logic and DB access
в”њв”Ђв”Ђ alembic/             # Database migrations
в”њв”Ђв”Ђ tests/               # pytest suite (isolated SQLite DB)
в”њв”Ђв”Ђ .github/workflows/   # GitHub Actions CI
в”њв”Ђв”Ђ Dockerfile
в”њв”Ђв”Ђ docker-compose.yml
в”њв”Ђв”Ђ requirements.txt
в”њв”Ђв”Ђ pyproject.toml       # ruff configuration
в”њв”Ђв”Ђ pytest.ini
в”њв”Ђв”Ђ .env.example
в””в”Ђв”Ђ README.md
```

## Getting Started

Create the `.env` file from the template:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

The API is then available at `http://localhost:8000`, with interactive Swagger
documentation at `http://localhost:8000/docs`.

## Running Tests

Inside Docker:

```bash
docker compose exec api pytest
```

Tests use an isolated in-memory SQLite database (see `tests/conftest.py`), so
they do not touch your PostgreSQL data.

## Linting

```bash
ruff check .
```

## API Overview

| Resource   | Endpoints |
|------------|-----------|
| Health     | `GET /health`, `GET /health/db` |
| Categories | `GET/POST /categories/`, `GET/PATCH/DELETE /categories/{id}` |
| Products   | `GET/POST /products/`, `GET/PATCH/DELETE /products/{id}` |
| Customers  | `GET/POST /customers/`, `GET/PATCH/DELETE /customers/{id}` |
| Orders     | `GET/POST /orders/`, `GET /orders/{id}`, `PATCH /orders/{id}/status` |

List endpoints support `skip` and `limit` query parameters (`limit` is capped
at 200). Products and orders also support filtering вЂ” see Swagger for details.

## Example: Creating an Order

```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
        "customer_id": 1,
        "items": [
          { "product_id": 1, "quantity": 2 }
        ],
        "notes": "First test order"
      }'
```

The API validates that the customer exists and is active, that each product
exists, is active, and has sufficient stock, and that no product is duplicated
within one order. On success it creates the order, decrements stock, records an
initial status-history entry, and returns the full order with its items.

## Notes on Design Decisions

* **Stock integrity.** Order creation locks each product row for the duration
  of the transaction, so two concurrent orders cannot both read the same stock
  level and oversell it.
* **Money.** Prices and totals use `Decimal` to avoid floating-point rounding
  errors in financial calculations.
* **Error handling.** Business-rule violations in the service layer raise a
  dedicated `OrderError`, which the router translates into a `400` response.

## Possible Extensions

JWT authentication, role-based access control, pagination metadata, full-text
search endpoints, and product/order soft-deletion.
