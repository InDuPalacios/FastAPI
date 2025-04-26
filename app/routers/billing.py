from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from models import Transaction, Invoice, TransactionCreate, Customer
from db import SessionDep

router = APIRouter()


# Endpoint to create a transaction
@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data: TransactionCreate, session:SessionDep):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get('customer_id'))
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detal="Customer dosen't exist")
    
    transaction_db = Transaction.model_validate(transaction_data_dict)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)
    
    return transaction_db


@router.get("/transactions")
async def list_transaction(session:SessionDep):
    query = select(Transaction)
    transaction = session.exec(query).all()
    return transaction


# Endpoint to create an invoice
@router.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
