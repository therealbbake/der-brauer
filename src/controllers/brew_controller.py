"""
Brew Controller for Der Brauer
Manages brewing process, timers, and temperature control
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..hardware.hardware_manager import HardwareManager

logger = logging.getLogger(__name__)

@dataclass
class Timer:
    """Brewing timer configuration"""
    id: str
    name: str
    duration_minutes: int
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    active: bool = False
    notified: bool = False

@dataclass
class TemperatureAlert:
    """Temperature alerting configuration"""
    id: str
    sensor_id: str
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    enabled: bool = True

class BrewController:
    """Main brewing process controller"""

    def __init__(self, hardware_manager: HardwareManager):
        self.hardware_manager = hardware_manager
        self.timers: Dict[str, Timer] = {}
        self.temperature_alerts: Dict[str, TemperatureAlert] = {}
        self.current_status = "idle"
        self.target_temperatures = {}  # device_id: target_temp
        self.brew_session_active = False

        # Start background monitoring task
        self._monitoring_task = asyncio.create_task(self._monitor_system())

    async def get_status(self) -> Dict[str, Any]:
        """Get current brewing system status"""
        sensor_data = await self.hardware_manager.get_sensor_data()

        # Get primary temperature sensor reading
        primary_temp = None
        for sensor_id, sensor_info in sensor_data.get("sensors", {}).items():
            if sensor_info.get("name", "").lower().find("primary") >= 0 or sensor_id == "mash_tun":
                primary_temp = sensor_info.get("value")
                break

        # If no primary found, use first temperature sensor
        if primary_temp is None:
            for sensor_id, sensor_info in sensor_data.get("sensors", {}).items():
                if sensor_info.get("unit") == "celsius":
                    primary_temp = sensor_info.get("value")
                    break

        return {
            "status": self.current_status,
            "temperature": primary_temp,
            "target_temperatures": self.target_temperatures,
            "brew_session_active": self.brew_session_active,
            "active_timers": len([t for t in self.timers.values() if t.active]),
            "timestamp": time.time()
        }

    async def set_timer(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set a brewing timer"""
        timer = Timer(
            id=config["id"],
            name=config.get("name", f"Timer {config['id']}"),
            duration_minutes=config["duration_minutes"]
        )

        if config.get("start_immediately", False):
            timer.start_time = time.time()
            timer.end_time = timer.start_time + (timer.duration_minutes * 60)
            timer.active = True

        self.timers[timer.id] = timer
        logger.info(f"Set timer: {timer.name} ({timer.duration_minutes} minutes)")
        return {"timer_id": timer.id, "success": True}

    async def get_timers(self) -> Dict[str, Any]:
        """Get all timers"""
        current_time = time.time()
        timer_list = []

        for timer in self.timers.values():
            remaining_seconds = 0
            if timer.active and timer.end_time:
                remaining_seconds = max(0, timer.end_time - current_time)

            timer_list.append({
                "id": timer.id,
                "name": timer.name,
                "duration_minutes": timer.duration_minutes,
                "active": timer.active,
                "remaining_seconds": int(remaining_seconds),
                "expired": timer.active and remaining_seconds == 0
            })

        return {"timers": timer_list}

    async def set_temperature_alert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set temperature alerting thresholds"""
        alert = TemperatureAlert(
            id=config["id"],
            sensor_id=config["sensor_id"],
            min_threshold=config.get("min_threshold"),
            max_threshold=config.get("max_threshold"),
            enabled=config.get("enabled", True)
        )

        self.temperature_alerts[alert.id] = alert
        logger.info(f"Set temperature alert for sensor {alert.sensor_id}")
        return {"alert_id": alert.id, "success": True}

    async def start_brew_session(self, recipe_id: str = None) -> Dict[str, Any]:
        """Start a brewing session"""
        self.brew_session_active = True
        self.current_status = "brewing"
        logger.info(f"Started brew session{' with recipe ' + recipe_id if recipe_id else ''}")
        return {"session_started": True, "recipe_id": recipe_id}

    async def stop_brew_session(self) -> Dict[str, Any]:
        """Stop the current brewing session"""
        self.brew_session_active = False
        self.current_status = "idle"
        self.target_temperature = None

        # Turn off all devices
        equipment = await self.hardware_manager.get_equipment_config()
        for device in equipment.get("devices", []):
            if device.get("state", False):
                await self.hardware_manager.control_device(device["id"], "off")

        logger.info("Stopped brew session")
        return {"session_stopped": True}

    async def set_target_temperature(self, temperature: float, device_id: str) -> Dict[str, Any]:
        """Set target temperature for a specific device"""
        if not device_id:
            raise ValueError("device_id is required")
        self.target_temperatures[device_id] = temperature
        await self._control_temperature(temperature, device_id)
        logger.info(f"Set target temperature to {temperature}°C for device {device_id}")
        return {"device_id": device_id, "target_temperature": temperature, "success": True}

    async def _monitor_system(self):
        """Background monitoring task"""
        while True:
            try:
                await self._check_timers()
                await self._check_temperature_alerts()
                for device_id, target_temp in list(self.target_temperatures.items()):
                    await self._control_temperature(target_temp, device_id)
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)

    async def _check_timers(self):
        """Check active timers and trigger notifications"""
        current_time = time.time()

        for timer in self.timers.values():
            if timer.active and timer.end_time and current_time >= timer.end_time:
                if not timer.notified:
                    timer.notified = True
                    timer.active = False
                    logger.warning(f"Timer expired: {timer.name}")

                    # Here you would trigger notifications (email, webhooks, etc.)
                    # For now, just log it

    async def _check_temperature_alerts(self):
        """Check temperature thresholds and trigger alerts"""
        sensor_data = await self.hardware_manager.get_sensor_data()

        for alert in self.temperature_alerts.values():
            if not alert.enabled:
                continue

            sensor_info = sensor_data.get("sensors", {}).get(alert.sensor_id)
            if not sensor_info:
                continue

            current_temp = sensor_info.get("value")
            if current_temp is None:
                continue

            alert_triggered = False
            alert_message = ""

            if alert.min_threshold is not None and current_temp < alert.min_threshold:
                alert_triggered = True
                alert_message = f"Temperature below minimum: {current_temp}°C < {alert.min_threshold}°C"
            elif alert.max_threshold is not None and current_temp > alert.max_threshold:
                alert_triggered = True
                alert_message = f"Temperature above maximum: {current_temp}°C > {alert.max_threshold}°C"

            if alert_triggered:
                logger.warning(f"Temperature alert for {alert.sensor_id}: {alert_message}")
                # Here you would trigger notifications

    async def _control_temperature(self, target_temp: float, heater_device_id: str):
        """Basic temperature control (placeholder for PID implementation)"""
        sensor_data = await self.hardware_manager.get_sensor_data()

        # Get the linked sensor for the device if available
        device = self.hardware_manager.devices.get(heater_device_id)
        sensor_id = device.linked_sensor_id if device and device.linked_sensor_id else None

        current_temp = None
        if sensor_id and sensor_id in sensor_data.get("sensors", {}):
            current_temp = sensor_data["sensors"][sensor_id].get("value")

        if current_temp is None:
            logger.warning("No temperature reading available for control. shutting off device for safety")
            await self.hardware_manager.control_device(heater_device_id, "off")
            return

        # Simple hysteresis control
        hysteresis = 0.5  # 0.5°C deadband

        if current_temp < (target_temp - hysteresis):
            # Turn heater on
            await self.hardware_manager.control_device(heater_device_id, "on")
        elif current_temp > (target_temp + hysteresis):
            # Turn heater off
            await self.hardware_manager.control_device(heater_device_id, "off")

    async def stop_temperature_control(self, device_id: str = None) -> Dict[str, Any]:
        """Stop temperature control for a specific device or all devices"""
        if device_id:
            if device_id in self.target_temperatures:
                await self.hardware_manager.control_device(device_id, "off")
                del self.target_temperatures[device_id]
                logger.info(f"Stopped temperature control for device {device_id}")
            return {"device_id": device_id, "success": True}
        else:
            for dev_id in list(self.target_temperatures.keys()):
                await self.hardware_manager.control_device(dev_id, "off")
            self.target_temperatures.clear()
            logger.info("Stopped temperature control for all devices")
            return {"success": True}

    async def cleanup(self):
        """Cleanup resources"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
