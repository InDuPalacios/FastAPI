# app/tests/tests_billing.py

from fastapi import status

def test_create_transaction(client):
    # First, create a customer
    customer_response = client.post(
        "/customers",
        json={
            "name": "Test Customer",
            "email": "testcustomer@example.com",
            "age": 30,
        },
    )
    assert customer_response.status_code == status.HTTP_201_CREATED
    customer_id = customer_response.json()["id"]

    # Create a transaction linked to the created customer
    transaction_response = client.post(
        "/transactions",
        json={
            "description": "Test transaction",
            "ammount": 100,
            "customer_id": customer_id,
        },
    )
    assert transaction_response.status_code == status.HTTP_201_CREATED
    transaction_data = transaction_response.json()
    assert transaction_data["description"] == "Test transaction"
    assert transaction_data["ammount"] == 100
    assert transaction_data["customer_id"] == customer_id


def test_list_transactions(client):
    # Make a request to list transactions
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert "items" in response_data
    assert "total_transactions" in response_data
    assert isinstance(response_data["items"], list)
    assert isinstance(response_data["total_transactions"], int)
