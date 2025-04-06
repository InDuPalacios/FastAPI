import zoneinfo
from datetime import datetime
from fastapi import FastAPI

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
