# StoreOps API

![CI](https://github.com/USERNAME/storeops-api/actions/workflows/ci.yml/badge.svg)

StoreOps API is a REST API for managing a small e-commerce back office:
categories, products, customers, orders, stock levels, and order status history.

It is built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**,
**Docker Compose**, and **pytest**.

> Replace `USERNAME` in the badge URL above with your GitHub username after
> creating the repository.

## Highlights

* Layered architecture: `routers` (HTTP) → `services` (business logic) → `models` (ORM).
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

Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy 2.0 · Alembic · Docker ·
Docker Compose · pytest · ruff

## Architecture

```text
HTTP request
    │
    ▼
routers/        validate input, map domain errors to HTTP status codes
    │
    ▼
services/       business logic, transactions, stock locking
    │
    ▼
models/         SQLAlchemy ORM entities
    │
    ▼
PostgreSQL
```

Request and response bodies are defined in `schemas/` (Pydantic). The database
session is provided per-request via the `get_db` dependency, which rolls back
on failure and always closes the session.

## Project Structure

```text
storeops-api/
├── app/
│   ├── main.py          # FastAPI app, root and health endpoints
│   ├── config.py        # Settings loaded from environment / .env
│   ├── database.py      # Engine, session factory, get_db dependency
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response models
│   ├── routers/         # API endpoints
│   └── services/        # Business logic and DB access
├── alembic/             # Database migrations
├── tests/               # pytest suite (isolated SQLite DB)
├── .github/workflows/   # GitHub Actions CI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml       # ruff configuration
├── pytest.ini
├── .env.example
└── README.md
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
at 200). Products and orders also support filtering — see Swagger for details.

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
