"""
Hardware Manager for Der Brauer
Manages sensors and controllable devices
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..database.service import DatabaseService

logger = logging.getLogger(__name__)

@dataclass
class Sensor:
    """Sensor configuration"""
    id: str
    name: str
    type: str  # temperature, pressure, flow
    pin: int
    address: Optional[str] = None
    enabled: bool = True
    nickname: Optional[str] = None  # User-friendly name

@dataclass
class Device:
    """Controllable device configuration"""
    id: str
    name: str
    type: str  # heater, pump, valve, kettle, fridge
    pin: int
    gpio_mode: str = "BCM"
    enabled: bool = True
    linked_sensor_id: Optional[str] = None  # For temperature-controlled devices

class HardwareManager:
    """Manages hardware sensors and controllable devices"""

    def __init__(self, temperature_unit: str = "celsius"):
        self.sensors: Dict[str, Sensor] = {}
        self.devices: Dict[str, Device] = {}
        self._gpio_initialized = False
        self._sensor_data_cache = {}
        self._device_states = {}
        self.temperature_unit = temperature_unit.lower()  # "celsius" or "fahrenheit"

        # Initialize GPIO (only on Raspberry Pi)
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self._gpio_initialized = True
            logger.info("GPIO initialized successfully")
        except ImportError:
            logger.warning("RPi.GPIO not available - running in simulation mode")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")

        # Load equipment from database
        asyncio.create_task(self._load_equipment_from_database())

    async def _load_equipment_from_database(self):
        """Load sensors and devices from database"""
        try:
            # Load sensors
            db_sensors = await DatabaseService.get_all_sensors()
            for db_sensor in db_sensors:
                sensor = Sensor(
                    id=db_sensor.id,
                    name=db_sensor.name,
                    nickname=db_sensor.nickname,
                    type=db_sensor.type,
                    pin=db_sensor.pin,
                    address=db_sensor.address,
                    enabled=db_sensor.enabled
                )
                self.sensors[sensor.id] = sensor

            # Load devices
            db_devices = await DatabaseService.get_all_devices()
            for db_device in db_devices:
                device = Device(
                    id=db_device.id,
                    name=db_device.name,
                    type=db_device.type,
                    pin=db_device.pin,
                    gpio_mode=db_device.gpio_mode,
                    enabled=db_device.enabled,
                    linked_sensor_id=db_device.linked_sensor_id
                )
                self.devices[device.id] = device
                self._device_states[device.id] = False

                # Initialize GPIO pin if available
                if self._gpio_initialized:
                    try:
                        import RPi.GPIO as GPIO
                        GPIO.setup(device.pin, GPIO.OUT)
                        GPIO.output(device.pin, GPIO.LOW)
                    except Exception as e:
                        logger.error(f"Failed to initialize device {device.id}: {e}")

            logger.info(f"Loaded {len(self.sensors)} sensors and {len(self.devices)} devices from database")

        except Exception as e:
            logger.error(f"Failed to load equipment from database: {e}")

    async def get_sensor_data(self) -> Dict[str, Any]:
        """Get current sensor readings"""
        sensor_data = {}

        for sensor_id, sensor in self.sensors.items():
            if not sensor.enabled:
                continue

            try:
                if sensor.type == "temperature":
                    reading = await self._read_temperature_sensor(sensor)
                elif sensor.type == "pressure":
                    reading = await self._read_pressure_sensor(sensor)
                elif sensor.type == "flow":
                    reading = await self._read_flow_sensor(sensor)
                else:
                    reading = None

                if reading is not None:
                    sensor_data[sensor_id] = {
                        "value": reading,
                        "unit": self._get_sensor_unit(sensor.type),
                        "timestamp": asyncio.get_event_loop().time(),
                        "name": sensor.name
                    }

            except Exception as e:
                logger.error(f"Error reading sensor {sensor_id}: {e}")

        return {"sensors": sensor_data}

    async def control_device(self, device_id: str, action: str, value: float = None) -> Dict[str, Any]:
        """Control a hardware device"""
        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]
        if not device.enabled:
            raise ValueError(f"Device {device_id} is disabled")

        try:
            if action == "on":
                await self._set_device_state(device, True)
                self._device_states[device_id] = True
            elif action == "off":
                await self._set_device_state(device, False)
                self._device_states[device_id] = False
            elif action == "set" and value is not None:
                # For PWM devices like heaters
                await self._set_device_value(device, value)
                self._device_states[device_id] = value
            else:
                raise ValueError(f"Invalid action: {action}")

            return {
                "device_id": device_id,
                "action": action,
                "value": value,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error controlling device {device_id}: {e}")
            return {
                "device_id": device_id,
                "action": action,
                "error": str(e),
                "success": False
            }

    async def discover_w1_sensors(self) -> Dict[str, Any]:
        """Discover all available W1 temperature sensors"""
        discovered_sensors = []

        try:
            # Check if running on Raspberry Pi
            if self._gpio_initialized:
                import os
                import glob

                # W1 devices are typically at /sys/bus/w1/devices/
                w1_base_dir = '/sys/bus/w1/devices/'
                if os.path.exists(w1_base_dir):
                    # Look for DS18B20 sensors (start with 28-)
                    sensor_dirs = glob.glob(os.path.join(w1_base_dir, '28-*'))
                    sensor_dirs.extend(glob.glob(os.path.join(w1_base_dir, '10-*')))  # DS18S20

                    for sensor_dir in sensor_dirs:
                        sensor_id = os.path.basename(sensor_dir)
                        discovered_sensors.append({
                            "id": sensor_id,
                            "address": sensor_id,
                            "type": "temperature",
                            "name": f"W1 Sensor {sensor_id[-6:]}",  # Last 6 chars for display
                            "discovered": True
                        })
                else:
                    logger.warning("W1 device directory not found")
            else:
                # Simulation mode - return mock sensors
                discovered_sensors = [
                    {"id": "28-000000000001", "address": "28-000000000001", "type": "temperature", "name": "Mock W1 Sensor 1", "discovered": True},
                    {"id": "28-000000000002", "address": "28-000000000002", "type": "temperature", "name": "Mock W1 Sensor 2", "discovered": True},
                ]
        except Exception as e:
            logger.error(f"Error discovering W1 sensors: {e}")

        return {"sensors": discovered_sensors}

    async def add_sensor(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new sensor"""
        # Save to database first
        db_sensor = await DatabaseService.create_sensor(config)

        # Create in-memory sensor object
        sensor = Sensor(
            id=db_sensor.id,
            name=db_sensor.name,
            type=db_sensor.type,
            pin=db_sensor.pin,
            address=db_sensor.address,
            enabled=db_sensor.enabled,
            nickname=db_sensor.nickname
        )

        self.sensors[sensor.id] = sensor
        logger.info(f"Added sensor: {sensor.id} (nickname: {sensor.nickname})")
        return {"sensor_id": sensor.id, "success": True}

    async def add_device(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new controllable device"""
        # Save to database first
        db_device = await DatabaseService.create_device(config)

        # Create in-memory device object
        device = Device(
            id=db_device.id,
            name=db_device.name,
            type=db_device.type,
            pin=db_device.pin,
            gpio_mode=db_device.gpio_mode,
            enabled=db_device.enabled,
            linked_sensor_id=db_device.linked_sensor_id
        )

        self.devices[device.id] = device
        self._device_states[device.id] = False

        # Initialize GPIO pin
        if self._gpio_initialized:
            try:
                import RPi.GPIO as GPIO
                GPIO.setup(device.pin, GPIO.OUT)
                GPIO.output(device.pin, GPIO.LOW)
            except Exception as e:
                logger.error(f"Failed to initialize device {device.id}: {e}")

        logger.info(f"Added device: {device.id} (linked to sensor: {device.linked_sensor_id})")
        return {"device_id": device.id, "success": True}

    async def update_sensor(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing sensor"""
        sensor_id = config.get("id")
        if not sensor_id or sensor_id not in self.sensors:
            raise ValueError(f"Sensor {sensor_id} not found")

        # Update in database first
        db_sensor = await DatabaseService.update_sensor(sensor_id, config)
        if not db_sensor:
            raise ValueError(f"Failed to update sensor {sensor_id} in database")

        # Update in-memory sensor object
        sensor = self.sensors[sensor_id]
        sensor.name = db_sensor.name
        sensor.nickname = db_sensor.nickname
        sensor.type = db_sensor.type
        sensor.pin = db_sensor.pin
        sensor.address = db_sensor.address
        sensor.enabled = db_sensor.enabled

        logger.info(f"Updated sensor: {sensor_id}")
        return {"sensor_id": sensor_id, "success": True}

    async def delete_sensor(self, sensor_id: str) -> Dict[str, Any]:
        """Delete a sensor"""
        if sensor_id not in self.sensors:
            raise ValueError(f"Sensor {sensor_id} not found")

        # Delete from database first
        success = await DatabaseService.delete_sensor(sensor_id)
        if not success:
            raise ValueError(f"Failed to delete sensor {sensor_id} from database")

        # Remove sensor from any linked devices
        for device in self.devices.values():
            if device.linked_sensor_id == sensor_id:
                device.linked_sensor_id = None

        # Remove the sensor
        del self.sensors[sensor_id]

        logger.info(f"Deleted sensor: {sensor_id}")
        return {"sensor_id": sensor_id, "success": True}

    async def update_device(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing device"""
        device_id = config.get("id")
        if not device_id or device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        # Update in database first
        db_device = await DatabaseService.update_device(device_id, config)
        if not db_device:
            raise ValueError(f"Failed to update device {device_id} in database")

        # Update in-memory device object
        device = self.devices[device_id]
        device.name = db_device.name
        device.type = db_device.type
        device.pin = db_device.pin
        device.gpio_mode = db_device.gpio_mode
        device.enabled = db_device.enabled
        device.linked_sensor_id = db_device.linked_sensor_id

        logger.info(f"Updated device: {device_id}")
        return {"device_id": device_id, "success": True}

    async def delete_device(self, device_id: str) -> Dict[str, Any]:
        """Delete a device"""
        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        # Delete from database first
        success = await DatabaseService.delete_device(device_id)
        if not success:
            raise ValueError(f"Failed to delete device {device_id} from database")

        # Turn off device before deleting
        if self._gpio_initialized and device_id in self._device_states:
            try:
                device = self.devices[device_id]
                import RPi.GPIO as GPIO
                GPIO.output(device.pin, GPIO.LOW)
            except Exception as e:
                logger.warning(f"Could not turn off device {device_id} before deletion: {e}")

        # Remove device state and device
        if device_id in self._device_states:
            del self._device_states[device_id]
        del self.devices[device_id]

        logger.info(f"Deleted device: {device_id}")
        return {"device_id": device_id, "success": True}

    async def get_equipment_config(self) -> Dict[str, Any]:
        """Get current equipment configuration"""
        return {
            "sensors": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.type,
                    "pin": s.pin,
                    "enabled": s.enabled
                } for s in self.sensors.values()
            ],
            "devices": [
                {
                    "id": d.id,
                    "name": d.name,
                    "type": d.type,
                    "pin": d.pin,
                    "enabled": d.enabled,
                    "state": self._device_states.get(d.id, False)
                } for d in self.devices.values()
            ]
        }

    # Private methods for sensor reading
    async def _read_temperature_sensor(self, sensor: Sensor) -> Optional[float]:
        """Read temperature from sensor"""
        if not self._gpio_initialized:
            return 20.0 + (hash(sensor.id) % 10)  # Simulated reading

        try:
            # DS18B20 temperature sensor reading
            if sensor.type == "temperature":
                # Placeholder - implement actual DS18B20 reading
                return 25.0  # Simulated
        except Exception as e:
            logger.error(f"Temperature sensor error: {e}")
            return None

    async def _read_pressure_sensor(self, sensor: Sensor) -> Optional[float]:
        """Read pressure from sensor"""
        if not self._gpio_initialized:
            return 14.7  # Simulated atmospheric pressure

        # Placeholder for pressure sensor implementation
        return 14.7

    async def _read_flow_sensor(self, sensor: Sensor) -> Optional[float]:
        """Read flow rate from sensor"""
        if not self._gpio_initialized:
            return 0.0  # No flow

        # Placeholder for flow sensor implementation
        return 0.0

    async def _set_device_state(self, device: Device, state: bool):
        """Set digital device state"""
        if not self._gpio_initialized:
            logger.info(f"Simulated setting device {device.id} to {state}")
            return

        try:
            import RPi.GPIO as GPIO
            GPIO.output(device.pin, GPIO.HIGH if state else GPIO.LOW)
        except Exception as e:
            logger.error(f"Device control error: {e}")
            raise

    async def _set_device_value(self, device: Device, value: float):
        """Set analog device value (PWM)"""
        if not self._gpio_initialized:
            logger.info(f"Simulated setting device {device.id} to {value}")
            return

        # Placeholder for PWM implementation
        pass

    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Get unit for sensor type"""
        if sensor_type == "temperature":
            return self.temperature_unit
        units = {
            "pressure": "psi",
            "flow": "liters_per_minute"
        }
        return units.get(sensor_type, "unknown")

    def set_temperature_unit(self, unit: str):
        """Set temperature unit preference"""
        unit = unit.lower()
        if unit not in ["celsius", "fahrenheit"]:
            raise ValueError("Temperature unit must be 'celsius' or 'fahrenheit'")
        self.temperature_unit = unit
        logger.info(f"Temperature unit set to {unit}")

    def convert_temperature(self, temperature: float, from_unit: str = "celsius", to_unit: str = None) -> float:
        """Convert temperature between Celsius and Fahrenheit"""
        if to_unit is None:
            to_unit = self.temperature_unit

        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit == to_unit:
            return temperature

        if from_unit == "celsius" and to_unit == "fahrenheit":
            return (temperature * 9/5) + 32
        elif from_unit == "fahrenheit" and to_unit == "celsius":
            return (temperature - 32) * 5/9
        else:
            raise ValueError(f"Unsupported temperature conversion: {from_unit} to {to_unit}")

    async def get_sensor_data(self, unit_override: str = None) -> Dict[str, Any]:
        """Get current sensor readings with optional unit override"""
        sensor_data = {}

        # Use unit override if provided, otherwise use instance setting
        temp_unit = unit_override or self.temperature_unit

        for sensor_id, sensor in self.sensors.items():
            if not sensor.enabled:
                continue

            try:
                if sensor.type == "temperature":
                    reading = await self._read_temperature_sensor(sensor)
                    if reading is not None and temp_unit != "celsius":
                        reading = self.convert_temperature(reading, "celsius", temp_unit)
                elif sensor.type == "pressure":
                    reading = await self._read_pressure_sensor(sensor)
                elif sensor.type == "flow":
                    reading = await self._read_flow_sensor(sensor)
                else:
                    reading = None

                if reading is not None:
                    sensor_data[sensor_id] = {
                        "value": reading,
                        "unit": self._get_sensor_unit(sensor.type, temp_unit),
                        "timestamp": asyncio.get_event_loop().time(),
                        "name": sensor.name
                    }

            except Exception as e:
                logger.error(f"Error reading sensor {sensor_id}: {e}")

        return {"sensors": sensor_data}

    def _get_sensor_unit(self, sensor_type: str, temp_unit: str = None) -> str:
        """Get unit for sensor type"""
        if temp_unit is None:
            temp_unit = self.temperature_unit

        if sensor_type == "temperature":
            return temp_unit
        units = {
            "pressure": "psi",
            "flow": "liters_per_minute"
        }
        return units.get(sensor_type, "unknown")
