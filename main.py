import zoneinfo
from datetime import datetime

from fastapi import FastAPI
from models import Customer, Transaction, Invoice


app = FastAPI()


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
@app.post("/customers")
async def create_customer(customer_data: Customer):
    return customer_data


# Endpoint to create a transaction
@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


# Endpoint to create an invoice
@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data