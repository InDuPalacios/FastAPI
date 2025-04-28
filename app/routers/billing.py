# ./app/routers/billing.py

# Importing External Modules
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select

# Importing Internal Modules
from models import Transaction, Invoice, TransactionCreate, Customer
from db import SessionDep

router = APIRouter()


# Endpoint to create a transaction
@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate, 
    session:SessionDep
):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get('customer_id'))
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detal="Customer dosen't exist"
        )
    transaction_db = Transaction.model_validate(transaction_data_dict)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)
    return transaction_db


# Endpoint to list transactions with pagination info
@router.get("/transactions")
async def list_transaction(
    session:SessionDep, 
    skip: int = Query(0, description="Records to skip"),
    limit: int= Query(10, description="Number of records to return")
):
    transactions_query = session.exec(select(Transaction))
    transactions = transactions_query.all()
    total = len(transactions)

    paginated_transactions = transactions[skip:skip + limit]

    return {
        "items": paginated_transactions,
        "total_transactions": total
    }


# Endpoint to create an invoice
@router.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
