"""
API Routes for Der Brauer
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..controllers.brew_controller import BrewController
from ..hardware.hardware_manager import HardwareManager

router = APIRouter()

# Initialize controllers (will be injected from main app)
brew_controller = None
hardware_manager = None

def init_controllers(bc: BrewController, hm: HardwareManager):
    """Initialize controllers for API routes"""
    global brew_controller, hardware_manager
    brew_controller = bc
    hardware_manager = hm

# Status and Monitoring Endpoints
@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get current brewing system status"""
    try:
        if brew_controller:
            return await brew_controller.get_status()
        return {"status": "idle", "message": "System not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensors")
async def get_sensor_data() -> Dict[str, Any]:
    """Get real-time sensor data"""
    try:
        if hardware_manager:
            return await hardware_manager.get_sensor_data()
        return {"sensors": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hardware Control Endpoints
@router.post("/hardware/{device_id}/control")
async def control_hardware_device(device_id: str, action: str, value: float = None):
    """Control hardware devices (heaters, pumps, etc.)"""
    try:
        if hardware_manager:
            return await hardware_manager.control_device(device_id, action, value)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Equipment Setup Endpoints
@router.get("/equipment")
async def get_equipment_config():
    """Get current equipment configuration"""
    try:
        if hardware_manager:
            return await hardware_manager.get_equipment_config()
        return {"equipment": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/equipment/sensor")
async def add_sensor(config: Dict[str, Any]):
    """Add a new sensor"""
    try:
        if hardware_manager:
            return await hardware_manager.add_sensor(config)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/equipment/device")
async def add_device(config: Dict[str, Any]):
    """Add a new controllable device"""
    try:
        if hardware_manager:
            return await hardware_manager.add_device(config)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/equipment/sensor/{sensor_id}")
async def update_sensor(sensor_id: str, config: Dict[str, Any]):
    """Update an existing sensor"""
    try:
        if hardware_manager:
            config["id"] = sensor_id  # Ensure ID is set
            return await hardware_manager.update_sensor(config)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/equipment/sensor/{sensor_id}")
async def delete_sensor(sensor_id: str):
    """Delete a sensor"""
    try:
        if hardware_manager:
            return await hardware_manager.delete_sensor(sensor_id)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/equipment/device/{device_id}")
async def update_device(device_id: str, config: Dict[str, Any]):
    """Update an existing device"""
    try:
        if hardware_manager:
            config["id"] = device_id  # Ensure ID is set
            return await hardware_manager.update_device(config)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/equipment/device/{device_id}")
async def delete_device(device_id: str):
    """Delete a device"""
    try:
        if hardware_manager:
            return await hardware_manager.delete_device(device_id)
        raise HTTPException(status_code=503, detail="Hardware manager not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Timer and Alerting Endpoints
@router.post("/timers")
async def set_timer(config: Dict[str, Any]):
    """Set a brewing timer"""
    try:
        if brew_controller:
            return await brew_controller.set_timer(config)
        raise HTTPException(status_code=503, detail="Brew controller not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timers")
async def get_timers():
    """Get active timers"""
    try:
        if brew_controller:
            return await brew_controller.get_timers()
        return {"timers": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/temperature")
async def set_temperature_alert(config: Dict[str, Any]):
    """Set temperature alerting thresholds"""
    try:
        if brew_controller:
            return await brew_controller.set_temperature_alert(config)
        raise HTTPException(status_code=503, detail="Brew controller not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sensor Discovery Endpoints
@router.get("/sensors/discover")
async def discover_sensors():
    """Discover available sensors on the system"""
    try:
        if hardware_manager:
            return await hardware_manager.discover_w1_sensors()
        return {"sensors": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
