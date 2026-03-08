#!/usr/bin/env python3
"""
Der Brauer - Main Application Entry Point
Raspberry Pi Brewing Control System
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .api.routes import router as api_router
from .controllers.brew_controller import BrewController
from .hardware.hardware_manager import HardwareManager
from .database.connection import init_database
import os

class TemperatureUnitRequest(BaseModel):
    unit: str

# Initialize FastAPI app
app = FastAPI(
    title="Der Brauer",
    description="Raspberry Pi Brewing Control System",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()
    print("Database initialized and ready")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize core components with configuration
temperature_unit = os.getenv("TEMPERATURE_UNIT", "celsius").lower()
if temperature_unit not in ["celsius", "fahrenheit"]:
    temperature_unit = "celsius"

hardware_manager = HardwareManager(temperature_unit=temperature_unit)
brew_controller = BrewController(hardware_manager)

# Initialize API controllers
from .api.routes import init_controllers
init_controllers(brew_controller, hardware_manager)

# Add temperature unit endpoints
@app.get("/api/v1/config/temperature-unit")
async def get_temperature_unit():
    """Get current temperature unit setting"""
    return {"temperature_unit": hardware_manager.temperature_unit}

@app.put("/api/v1/config/temperature-unit")
async def set_temperature_unit(request: TemperatureUnitRequest):
    """Set temperature unit preference"""
    try:
        hardware_manager.set_temperature_unit(request.unit)
        return {"temperature_unit": hardware_manager.temperature_unit, "success": True}
    except ValueError as e:
        return {"error": str(e), "success": False}

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Web UI routes
@app.get("/")
async def root(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/setup")
async def setup(request: Request):
    """Equipment setup interface"""
    return templates.TemplateResponse("setup.html", {"request": request})

@app.get("/control")
async def control(request: Request):
    """Manual control panel"""
    return templates.TemplateResponse("control.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """Brew monitoring dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
