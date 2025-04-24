import zoneinfo
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from models import Customer, CustomerCreate, Transaction, Invoice, CustomerUpdate
from db import SessionDep, create_all_tables
from sqlmodel import select


app = FastAPI(lifespan= create_all_tables)


# Root endpoint returns a simple welcome message
@app.get("/")
async def root():
    return {"message": "Hello World!"}


# Dictionary mapping ISO country codes to timezone strings
country_timezones = {
    "CO": {"timezone": "America/Bogota", "name": "Colombia"},
    "MX": {"timezone": "America/Mexico_City", "name": "México"},
    "AR": {"timezone": "America/Argentina/Buenos_Aires", "name": "Argentina"},
    "BR": {"timezone": "America/Sao_Paulo", "name": "Brasil"},
    "PE": {"timezone": "America/Lima", "name": "Perú"},
}


# Endpoint to return the current time based on ISO country code
@app.get("/time/{iso_code}")
async def time(iso_code: str):
    iso = iso_code.upper()
    data = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(data["timezone"])
    now = datetime.now(tz)

    return {
        "message": f"Estás viendo la hora actual en {data['name']}.",
        "time": now.strftime("%Y-%m-%d %H:%M:%S")
    }


# Endpoint to list all registered customers
@app.post("/customers", response_model= Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# Endpoint to list all registered customers
@app.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()


# Endpoint to get a single customer by ID
@app.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found")
    return customer


# Endpoint to delete a specific customer by ID
@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found")
    session.delete(customer)
    session.commit()
    return {"detal":"ok"}


# Endpoint to update an existing customer by ID
@app.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: int,
    updated_data: CustomerUpdate,
    session: SessionDep
):
    customer = session.get(Customer, customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Extract only the fields that were provided (non-null values)
    customer_data = updated_data.model_dump(exclude_unset=True)

    for key, value in customer_data.items():
        setattr(customer, key, value)

    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer


# Endpoint to create a transaction
@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


# Endpoint to create an invoice
@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data