import zoneinfo
from datetime import datetime

from fastapi import FastAPI
from db import create_all_tables
from .routers import customers, billing, plans


app = FastAPI(lifespan= create_all_tables)
app.include_router(customers.router)
app.include_router(billing.router, tags=["billing"]) 
app.include_router(plans.router, tags=["plans"])


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
