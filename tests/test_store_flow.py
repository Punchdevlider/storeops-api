from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_full_store_flow():
    unique_id = uuid4().hex[:8]

    # 1. Create category
    category_response = client.post(
        "/categories/",
        json={
            "name": f"Test Category {unique_id}",
            "description": "Category created during automated test",
        },
    )

    assert category_response.status_code == 201

    category = category_response.json()
    assert category["name"] == f"Test Category {unique_id}"

    category_id = category["id"]

    # 2. Create product
    product_response = client.post(
        "/products/",
        json={
            "name": f"Test Product {unique_id}",
            "sku": f"SKU-{unique_id}",
            "description": "Product created during automated test",
            "price": "19.99",
            "stock_quantity": 10,
            "is_active": True,
            "category_id": category_id,
        },
    )

    assert product_response.status_code == 201

    product = product_response.json()
    assert product["sku"] == f"SKU-{unique_id}"
    assert product["stock_quantity"] == 10

    product_id = product["id"]

    # 3. Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "first_name": "Test",
            "last_name": "Customer",
            "email": f"customer-{unique_id}@example.com",
            "phone": "+380501112233",
            "is_active": True,
        },
    )

    assert customer_response.status_code == 201

    customer = customer_response.json()
    assert customer["email"] == f"customer-{unique_id}@example.com"

    customer_id = customer["id"]

    # 4. Create order
    order_response = client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
            "notes": "Order created during automated test",
        },
    )

    assert order_response.status_code == 201

    order = order_response.json()
    assert order["customer_id"] == customer_id
    assert order["status"] == "pending"
    assert order["total_amount"] == "39.98"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2

    order_id = order["id"]

    # 5. Check product stock was decreased
    updated_product_response = client.get(f"/products/{product_id}")

    assert updated_product_response.status_code == 200

    updated_product = updated_product_response.json()
    assert updated_product["stock_quantity"] == 8

    # 6. Update order status
    status_response = client.patch(
        f"/orders/{order_id}/status",
        json={
            "status": "processing",
        },
    )

    assert status_response.status_code == 200

    updated_order = status_response.json()
    assert updated_order["status"] == "processing"
    assert len(updated_order["status_history"]) >= 2