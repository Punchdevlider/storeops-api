from uuid import uuid4


def test_full_store_flow(client):
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

def _create_product(client, unique_id, stock=10, is_active=True):
    category = client.post(
        "/categories/",
        json={"name": f"Cat {unique_id}", "description": "test"},
    ).json()

    return client.post(
        "/products/",
        json={
            "name": f"Product {unique_id}",
            "sku": f"SKU-{unique_id}",
            "price": "19.99",
            "stock_quantity": stock,
            "is_active": is_active,
            "category_id": category["id"],
        },
    ).json()


def _create_customer(client, unique_id):
    return client.post(
        "/customers/",
        json={
            "first_name": "Test",
            "last_name": "Customer",
            "email": f"customer-{unique_id}@example.com",
            "is_active": True,
        },
    ).json()


def test_order_with_missing_product_returns_404(client):
    unique_id = uuid4().hex[:8]
    customer = _create_customer(client, unique_id)

    response = client.post(
        "/orders/",
        json={
            "customer_id": customer["id"],
            "items": [{"product_id": 999999, "quantity": 1}],
        },
    )

    assert response.status_code == 404


def test_order_exceeding_stock_is_rejected(client):
    unique_id = uuid4().hex[:8]
    product = _create_product(client, unique_id, stock=3)
    customer = _create_customer(client, unique_id)

    response = client.post(
        "/orders/",
        json={
            "customer_id": customer["id"],
            "items": [{"product_id": product["id"], "quantity": 5}],
        },
    )

    assert response.status_code == 400


def test_duplicate_products_in_order_are_rejected(client):
    unique_id = uuid4().hex[:8]
    product = _create_product(client, unique_id, stock=10)
    customer = _create_customer(client, unique_id)

    response = client.post(
        "/orders/",
        json={
            "customer_id": customer["id"],
            "items": [
                {"product_id": product["id"], "quantity": 1},
                {"product_id": product["id"], "quantity": 1},
            ],
        },
    )

    assert response.status_code == 400
