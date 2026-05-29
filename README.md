# StoreOps API

StoreOps API is a Python REST API for managing e-commerce products, categories, customers, orders, stock levels, and order status history.

The project is built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose, and pytest.

## Features

* Category CRUD
* Product CRUD
* Customer CRUD
* Order creation
* Product stock validation
* Automatic stock reduction after order creation
* Order status updates
* Order status history
* PostgreSQL database
* SQLAlchemy ORM
* Alembic migrations
* Dockerized development environment
* Automated tests with pytest
* Swagger API documentation

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Docker
* Docker Compose
* Pytest

## Project Structure

```text
storeops-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Run Project

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Start the project:

```bash
docker compose up --build
```

API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Run Migrations

```bash
docker compose exec api alembic upgrade head
```

## Run Tests

```bash
docker compose exec api pytest
```

## API Endpoints

### Health

```text
GET /health
GET /health/db
```

### Categories

```text
GET    /categories/
POST   /categories/
GET    /categories/{category_id}
PATCH  /categories/{category_id}
DELETE /categories/{category_id}
```

### Products

```text
GET    /products/
POST   /products/
GET    /products/{product_id}
PATCH  /products/{product_id}
DELETE /products/{product_id}
```

### Customers

```text
GET    /customers/
POST   /customers/
GET    /customers/{customer_id}
PATCH  /customers/{customer_id}
DELETE /customers/{customer_id}
```

### Orders

```text
GET   /orders/
POST  /orders/
GET   /orders/{order_id}
PATCH /orders/{order_id}/status
```

## Example Order Request

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "notes": "First test order"
}
```

## Status

Current version includes core e-commerce API functionality with Dockerized PostgreSQL, migrations, and automated tests.

Planned improvements:

* JWT authentication
* Role-based access control
* Separate test database
* Pagination metadata
* Search endpoints
* GitHub Actions CI

```
```
