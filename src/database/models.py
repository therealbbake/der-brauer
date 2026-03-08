"""
Database models for Der Brauer
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Sensor(Base):
    """Sensor configuration and metadata"""
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    type = Column(String, nullable=False)  # temperature, pressure, flow
    pin = Column(Integer, nullable=False)
    address = Column(String, nullable=True)  # For I2C, W1 sensors
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id='{self.id}', name='{self.name}', type='{self.type}')>"

class Device(Base):
    """Controllable device configuration"""
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # heater, pump, valve, kettle, fridge
    pin = Column(Integer, nullable=False)
    gpio_mode = Column(String, default="BCM")
    enabled = Column(Boolean, default=True)
    linked_sensor_id = Column(String, ForeignKey("sensors.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    linked_sensor = relationship("Sensor", foreign_keys=[linked_sensor_id])

    def __repr__(self):
        return f"<Device(id='{self.id}', name='{self.name}', type='{self.type}')>"

class SensorReading(Base):
    """Historical sensor readings"""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")

    def __repr__(self):
        return f"<SensorReading(sensor_id='{self.sensor_id}', value={self.value}, unit='{self.unit}')>"

class DeviceState(Base):
    """Device state history"""
    __tablename__ = "device_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False, index=True)
    state = Column(Boolean, nullable=False)  # True = ON, False = OFF
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<DeviceState(device_id='{self.device_id}', state={self.state})>"

class Configuration(Base):
    """Application configuration settings"""
    __tablename__ = "configuration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Configuration(key='{self.key}', value='{self.value}')>"

class Timer(Base):
    """Brewing timer configuration"""
    __tablename__ = "timers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    active = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Timer(id='{self.id}', name='{self.name}', active={self.active})>"

class TemperatureAlert(Base):
    """Temperature alerting configuration"""
    __tablename__ = "temperature_alerts"

    id = Column(String, primary_key=True, index=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TemperatureAlert(id='{self.id}', sensor_id='{self.sensor_id}')>"

class BrewSession(Base):
    """Brewing session tracking"""
    __tablename__ = "brew_sessions"

    id = Column(String, primary_key=True, index=True)
    recipe_id = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, completed, cancelled
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<BrewSession(id='{self.id}', status='{self.status}')>"

class SystemLog(Base):
    """System event logging"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SystemLog(level='{self.level}', component='{self.component}')>"