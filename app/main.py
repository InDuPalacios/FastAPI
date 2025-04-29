# ./app/main.py

# Importing External Modules
import time
import zoneinfo
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from sqlalchemy.orm import Session

# Importing Internal Modules
from db import create_all_tables, SessionDep
from .routers import customers, billing, plans
from .utils.utils import hash_password, verify_password 
from models import CustomerCreate, Customer

app = FastAPI(lifespan= create_all_tables)
security = HTTPBasic()

app.include_router(customers.router, tags=['customers'])
app.include_router(billing.router, tags=["billing"]) 
app.include_router(plans.router, tags=["plans"])


# Endpoint to authenticate the user using HTTP Basic Authentication
@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == "indu" and credentials.password == "1234":
        return {"mensaje": f"Hola, {credentials.username}"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    star_time = time.time()
    response = await call_next(request)
    process_time = time.time() - star_time
    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")
    return response


@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    # Print all headers
    print("Headers received:")
    for name, value in request.headers.items():
        print(f"{name}: {value}")

    response = await call_next(request)
    return response



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
async def get_time_by_iso_code(iso_code: str):
    iso = iso_code.upper()
    data = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(data["timezone"])
    now = datetime.now(tz)

    return {
        "message": f"Estás viendo la hora actual en {data['name']}.",
        "time": now.strftime("%Y-%m-%d %H:%M:%S")
    }
