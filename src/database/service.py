"""
Database service for Der Brauer
Provides high-level database operations
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, and_, or_
from datetime import datetime, timedelta

from .models import (
    Sensor, Device, SensorReading, DeviceState,
    Configuration, Timer, TemperatureAlert, BrewSession, SystemLog
)
from .connection import async_session

logger = logging.getLogger(__name__)

class DatabaseService:
    """High-level database operations service"""

    @staticmethod
    async def get_session() -> AsyncSession:
        """Get database session"""
        return async_session()

    # Sensor Operations
    @staticmethod
    async def get_all_sensors() -> List[Sensor]:
        """Get all sensors"""
        async with async_session() as session:
            result = await session.execute(select(Sensor))
            return result.scalars().all()

    @staticmethod
    async def get_sensor_by_id(sensor_id: str) -> Optional[Sensor]:
        """Get sensor by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(Sensor).where(Sensor.id == sensor_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create_sensor(sensor_data: Dict[str, Any]) -> Sensor:
        """Create a new sensor"""
        async with async_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            await session.commit()
            await session.refresh(sensor)
            logger.info(f"Created sensor: {sensor.id}")
            return sensor

    @staticmethod
    async def update_sensor(sensor_id: str, sensor_data: Dict[str, Any]) -> Optional[Sensor]:
        """Update an existing sensor"""
        async with async_session() as session:
            result = await session.execute(
                select(Sensor).where(Sensor.id == sensor_id)
            )
            sensor = result.scalar_one_or_none()

            if sensor:
                for key, value in sensor_data.items():
                    if hasattr(sensor, key):
                        setattr(sensor, key, value)

                sensor.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(sensor)
                logger.info(f"Updated sensor: {sensor_id}")

            return sensor

    @staticmethod
    async def delete_sensor(sensor_id: str) -> bool:
        """Delete a sensor"""
        async with async_session() as session:
            result = await session.execute(
                select(Sensor).where(Sensor.id == sensor_id)
            )
            sensor = result.scalar_one_or_none()

            if sensor:
                await session.delete(sensor)
                await session.commit()
                logger.info(f"Deleted sensor: {sensor_id}")
                return True

            return False

    # Device Operations
    @staticmethod
    async def get_all_devices() -> List[Device]:
        """Get all devices"""
        async with async_session() as session:
            result = await session.execute(select(Device))
            return result.scalars().all()

    @staticmethod
    async def get_device_by_id(device_id: str) -> Optional[Device]:
        """Get device by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(Device).where(Device.id == device_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create_device(device_data: Dict[str, Any]) -> Device:
        """Create a new device"""
        async with async_session() as session:
            device = Device(**device_data)
            session.add(device)
            await session.commit()
            await session.refresh(device)
            logger.info(f"Created device: {device.id}")
            return device

    @staticmethod
    async def update_device(device_id: str, device_data: Dict[str, Any]) -> Optional[Device]:
        """Update an existing device"""
        async with async_session() as session:
            result = await session.execute(
                select(Device).where(Device.id == device_id)
            )
            device = result.scalar_one_or_none()

            if device:
                for key, value in device_data.items():
                    if hasattr(device, key):
                        setattr(device, key, value)

                device.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(device)
                logger.info(f"Updated device: {device_id}")

            return device

    @staticmethod
    async def delete_device(device_id: str) -> bool:
        """Delete a device"""
        async with async_session() as session:
            result = await session.execute(
                select(Device).where(Device.id == device_id)
            )
            device = result.scalar_one_or_none()

            if device:
                await session.delete(device)
                await session.commit()
                logger.info(f"Deleted device: {device_id}")
                return True

            return False

    # Sensor Reading Operations
    @staticmethod
    async def save_sensor_reading(sensor_id: str, value: float, unit: str) -> SensorReading:
        """Save a sensor reading"""
        async with async_session() as session:
            reading = SensorReading(
                sensor_id=sensor_id,
                value=value,
                unit=unit
            )
            session.add(reading)
            await session.commit()
            await session.refresh(reading)
            return reading

    @staticmethod
    async def get_sensor_readings(sensor_id: str, limit: int = 100) -> List[SensorReading]:
        """Get recent sensor readings for a sensor"""
        async with async_session() as session:
            result = await session.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id == sensor_id)
                .order_by(desc(SensorReading.timestamp))
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_recent_sensor_readings(hours: int = 24) -> List[SensorReading]:
        """Get all sensor readings from the last N hours"""
        since_time = datetime.utcnow() - timedelta(hours=hours)
        async with async_session() as session:
            result = await session.execute(
                select(SensorReading)
                .where(SensorReading.timestamp >= since_time)
                .order_by(desc(SensorReading.timestamp))
            )
            return result.scalars().all()

    # Device State Operations
    @staticmethod
    async def save_device_state(device_id: str, state: bool) -> DeviceState:
        """Save a device state change"""
        async with async_session() as session:
            device_state = DeviceState(
                device_id=device_id,
                state=state
            )
            session.add(device_state)
            await session.commit()
            await session.refresh(device_state)
            return device_state

    @staticmethod
    async def get_device_states(device_id: str, limit: int = 50) -> List[DeviceState]:
        """Get recent device state history"""
        async with async_session() as session:
            result = await session.execute(
                select(DeviceState)
                .where(DeviceState.device_id == device_id)
                .order_by(desc(DeviceState.timestamp))
                .limit(limit)
            )
            return result.scalars().all()

    # Configuration Operations
    @staticmethod
    async def get_config_value(key: str) -> Optional[str]:
        """Get configuration value by key"""
        async with async_session() as session:
            result = await session.execute(
                select(Configuration.value).where(Configuration.key == key)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def set_config_value(key: str, value: str, description: str = None) -> Configuration:
        """Set configuration value"""
        async with async_session() as session:
            # Check if config exists
            result = await session.execute(
                select(Configuration).where(Configuration.key == key)
            )
            config = result.scalar_one_or_none()

            if config:
                config.value = value
                if description:
                    config.description = description
            else:
                config = Configuration(
                    key=key,
                    value=value,
                    description=description
                )
                session.add(config)

            await session.commit()
            await session.refresh(config)
            return config

    @staticmethod
    async def get_all_config() -> List[Configuration]:
        """Get all configuration settings"""
        async with async_session() as session:
            result = await session.execute(select(Configuration))
            return result.scalars().all()

    # Timer Operations
    @staticmethod
    async def get_all_timers() -> List[Timer]:
        """Get all timers"""
        async with async_session() as session:
            result = await session.execute(select(Timer))
            return result.scalars().all()

    @staticmethod
    async def get_timer_by_id(timer_id: str) -> Optional[Timer]:
        """Get timer by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(Timer).where(Timer.id == timer_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create_timer(timer_data: Dict[str, Any]) -> Timer:
        """Create a new timer"""
        async with async_session() as session:
            timer = Timer(**timer_data)
            session.add(timer)
            await session.commit()
            await session.refresh(timer)
            return timer

    @staticmethod
    async def update_timer(timer_id: str, timer_data: Dict[str, Any]) -> Optional[Timer]:
        """Update an existing timer"""
        async with async_session() as session:
            result = await session.execute(
                select(Timer).where(Timer.id == timer_id)
            )
            timer = result.scalar_one_or_none()

            if timer:
                for key, value in timer_data.items():
                    if hasattr(timer, key):
                        setattr(timer, key, value)

                await session.commit()
                await session.refresh(timer)

            return timer

    @staticmethod
    async def delete_timer(timer_id: str) -> bool:
        """Delete a timer"""
        async with async_session() as session:
            result = await session.execute(
                select(Timer).where(Timer.id == timer_id)
            )
            timer = result.scalar_one_or_none()

            if timer:
                await session.delete(timer)
                await session.commit()
                return True

            return False

    # Temperature Alert Operations
    @staticmethod
    async def get_all_temperature_alerts() -> List[TemperatureAlert]:
        """Get all temperature alerts"""
        async with async_session() as session:
            result = await session.execute(select(TemperatureAlert))
            return result.scalars().all()

    @staticmethod
    async def create_temperature_alert(alert_data: Dict[str, Any]) -> TemperatureAlert:
        """Create a new temperature alert"""
        async with async_session() as session:
            alert = TemperatureAlert(**alert_data)
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert

    # System Logging
    @staticmethod
    async def log_system_event(level: str, message: str, component: str = None):
        """Log a system event"""
        async with async_session() as session:
            log_entry = SystemLog(
                level=level,
                message=message,
                component=component
            )
            session.add(log_entry)
            await session.commit()

    @staticmethod
    async def get_system_logs(limit: int = 100, level: str = None) -> List[SystemLog]:
        """Get recent system logs"""
        async with async_session() as session:
            query = select(SystemLog).order_by(desc(SystemLog.timestamp))

            if level:
                query = query.where(SystemLog.level == level)

            query = query.limit(limit)

            result = await session.execute(query)
            return result.scalars().all()