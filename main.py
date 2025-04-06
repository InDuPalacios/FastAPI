import zoneinfo
from datetime import datetime

from fastapi import FastAPI
from models import Customer, CustomerCreate, Transaction, Invoice
from db import SessionDep

app = FastAPI()


# Root endpoint returns a simple welcome message
@app.get("/")
async def root():
    return {"message": "Hello World!"}


# Dictionary mapping ISO country codes to timezone strings
country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}


# Endpoint to return the current time based on ISO country code
@app.get("/time/{iso_code}")
async def time(iso_code: str):
    iso = iso_code.upper()  # Convert input to uppercase for consistency
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    return{"time": datetime.now(tz)}


# In-memory customer storage (simulates a database)
db_customers: list[Customer] = []


# Endpoint to create a customer with validated input
@app.post("/customers", response_model = Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    customer.id = len(db_customers)  # Simulate auto-incremented ID
    db_customers.append(customer)
    return customer


# Endpoint to list all registered customers
@app.get("/customers", response_model=list[Customer])
async def list_customer():
    return db_customers


# Endpoint to create a transaction
@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


# Endpoint to create an invoice
@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
