# Der Brauer Technical Design Document

## Introduction
This document provides a detailed technical breakdown of the Der Brauer brewing control system. It covers the key components, data flows, and implementation details of how the service operates, with a focus on the core brewing control logic, hardware integration, API, and user interface.

## System Components

### 1. Hardware Manager (src/hardware/hardware_manager.py)
- **Purpose**: Interfaces with physical hardware including sensors and actuators via GPIO on Raspberry Pi.
- **Key Features**:
  - Sensor management: Supports temperature, pressure, and flow sensors. Uses 1-Wire for DS18B20 sensors.
  - Device control: Manages heaters, pumps, valves, etc., with on/off and PWM control.
  - Linked sensors: Devices can be linked to specific sensors for targeted control (e.g., a heater linked to a temperature sensor).
  - Discovery: Auto-discovers W1 temperature sensors.
  - Simulation mode: Runs without actual GPIO for development.
- **Data Flow**: Loads configurations from database on init. Provides async methods for reading sensors and controlling devices.

### 2. Brew Controller (src/controllers/brew_controller.py)
- **Purpose**: Core logic for brewing processes, including timers, alerts, and temperature control.
- **Key Features**:
  - Background monitoring loop: Runs every 5 seconds to check timers, temperature alerts, and perform temperature control.
  - Timers: Configurable timers with notifications on expiration.
  - Temperature Alerts: Threshold-based alerts for sensors.
  - Multi-Device Temperature Control:
    - Uses a dictionary to track target temperatures per device.
    - Hysteresis control (0.5°C deadband) to turn devices on/off based on current vs target temperature.
    - Prefers linked sensor readings; falls back to primary temperature sensor.
  - Session Management: Start/stop brew sessions, turning off all devices on stop.
- **Data Flow**: Interacts with Hardware Manager for sensor data and device control. Exposes methods for API integration.

### 3. API Routes (src/api/routes.py)
- **Purpose**: Exposes RESTful endpoints using FastAPI for all system interactions.
- **Key Endpoints**:
  - Status: GET /status - Returns current system status including temperatures and targets.
  - Sensors: GET /sensors - Real-time sensor data.
  - Equipment: GET/POST/PUT/DELETE for sensors and devices.
  - Timers: POST/GET for setting and retrieving timers.
  - Alerts: POST for temperature alerts.
  - Temperature Control: POST /temperature/set and /temperature/stop - Supports per-device or all devices.
  - Hardware Control: POST /hardware/{device_id}/control - Direct device actions.
- **Data Flow**: Routes initialize with BrewController and HardwareManager instances. All operations are async.

### 4. User Interface (templates/*.html, static/js/app.js)
- **Purpose**: Provides a web-based UI for monitoring and control using Jinja2 templates and Bootstrap.
- **Key Pages**:
  - Dashboard: Real-time status monitoring.
  - Control: Manual device control, timers, temperature setting, and alerts.
  - Setup: Equipment configuration with sensor discovery.
- **JavaScript Logic**:
  - Uses fetch for API calls.
  - Real-time updates via intervals (e.g., loadDevices every 10s).
  - Temperature unit handling with conversions.
  - Per-device temperature set/stop buttons in device cards.
  - Global stop for temperature control.
- **Data Flow**: Frontend polls API endpoints for data and sends POST requests for controls.

### 5. Database (src/database/*)
- **Purpose**: Persists equipment configurations using SQLite.
- **Models**: Sensor and Device models.
- **Services**: CRUD operations for sensors and devices.
- **Data Flow**: Hardware Manager loads from DB on init; changes persist to DB.

## Key Processes

### Temperature Control Flow
1. User sets target via UI -> API POST /temperature/set -> BrewController.set_target_temperature.
2. Stores target in self.target_temperatures dict.
3. Monitoring loop calls _control_temperature for each device every 5s.
4. Reads current temp from linked or primary sensor.
5. Applies hysteresis: If below target - hysteresis, turn on; if above target + hysteresis, turn off.
6. Stop: UI calls API POST /temperature/stop (with or without device_id) -> BrewController.stop_temperature_control -> Turns off device and removes from dict.

### Multi-Device Support
- Targets stored per device_id in a dictionary.
- Loop iterates over all entries independently.
- Stop can target specific device or clear all.

### Background Monitoring
- Async task runs infinite loop.
- Checks timers for expiration.
- Checks alerts against current sensor data.
- Performs temperature control for all active devices.

## Safety and Error Handling
- Emergency stop in UI turns off critical devices.
- Logging for all operations.
- Fallbacks for sensor readings.
- Simulation mode for non-RPi development.

## Future Improvements
- PID control instead of hysteresis.
- WebSocket for real-time updates.
- Authentication and remote access.

This design ensures a robust, extensible system for home brewing control.