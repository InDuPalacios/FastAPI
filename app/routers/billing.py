from fastapi import APIRouter
from models import Transaction, Invoice

router = APIRouter()

# Endpoint to create a transaction
@router.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


# Endpoint to create an invoice
@router.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
