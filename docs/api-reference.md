# Der Brauer API Reference

## Overview
The Der Brauer API provides REST endpoints for controlling and monitoring the brewing process. All endpoints return JSON responses.

Base URL: `http://localhost:8000/api/v1`

## Authentication
Currently no authentication required (local network only). Future versions will include API key authentication.

## Endpoints

### System Configuration

#### GET /config/temperature-unit
Get current temperature unit setting.

**Response:**
```json
{
  "temperature_unit": "celsius"
}
```

#### PUT /config/temperature-unit
Set temperature unit preference.

**Request Body:**
```json
"fahrenheit"
```

**Response:**
```json
{
  "temperature_unit": "fahrenheit",
  "success": true
}
```

### Status and Monitoring

#### GET /status
Get current brewing system status.

**Response:**
```json
{
  "status": "idle",
  "temperature": 25.5,
  "target_temperature": null,
  "brew_session_active": false,
  "active_timers": 0,
  "timestamp": 1696182600.123
}
```

#### GET /sensors
Get real-time sensor data.

**Response:**
```json
{
  "sensors": {
    "temp_mash": {
      "value": 68.5,
      "unit": "celsius",
      "timestamp": 1696182600.123,
      "name": "Mash Tun"
    }
  }
}
```

#### GET /sensors/discover
Discover available W1 temperature sensors on the system.

**Response:**
```json
{
  "sensors": [
    {
      "id": "28-000000000001",
      "address": "28-000000000001",
      "type": "temperature",
      "name": "W1 Sensor 000001",
      "discovered": true
    }
  ]
}
```

#### GET /logs
Get system logs.

**Query Parameters:**
- `limit` (optional): Number of log entries to return (default: 100)
- `level` (optional): Log level filter (DEBUG, INFO, WARNING, ERROR)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2023-10-01T14:30:00Z",
      "level": "INFO",
      "message": "Brewing process started",
      "component": "controller"
    }
  ]
}
```

### Recipe Management

#### GET /recipes
List all available recipes.

**Response:**
```json
{
  "recipes": [
    {
      "id": "pale_ale_v1",
      "name": "Pale Ale v1.0",
      "description": "Classic American Pale Ale",
      "stages": [
        {
          "name": "Mashing",
          "duration_minutes": 60,
          "target_temperature": 67.0
        }
      ],
      "created_at": "2023-09-15T10:00:00Z",
      "updated_at": "2023-09-15T10:00:00Z"
    }
  ]
}
```

#### POST /recipes
Create a new recipe.

**Request Body:**
```json
{
  "name": "New Recipe",
  "description": "Description of the recipe",
  "stages": [
    {
      "name": "Stage Name",
      "duration_minutes": 60,
      "target_temperature": 67.0,
      "instructions": "Optional instructions"
    }
  ]
}
```

**Response:** Same as GET /recipes/{id}

#### GET /recipes/{id}
Get a specific recipe by ID.

#### PUT /recipes/{id}
Update a recipe.

#### DELETE /recipes/{id}
Delete a recipe.

### Brewing Control

#### POST /brewing/start
Start a brewing session.

**Request Body:**
```json
{
  "recipe_id": "pale_ale_v1",
  "batch_size_liters": 20
}
```

**Response:**
```json
{
  "session_id": "brew_20231001_001",
  "status": "starting",
  "estimated_duration_hours": 8
}
```

#### POST /brewing/stop
Stop the current brewing session.

**Response:**
```json
{
  "status": "stopped",
  "message": "Brewing session stopped safely"
}
```

#### POST /brewing/pause
Pause the current brewing session.

#### POST /brewing/resume
Resume a paused brewing session.

#### GET /brewing/current
Get current brewing session details.

### Equipment Management

#### GET /equipment
Get current equipment configuration.

**Response:**
```json
{
  "sensors": [
    {
      "id": "temp_mash",
      "name": "Mash Tun",
      "nickname": "Primary Mash",
      "type": "temperature",
      "pin": 4,
      "enabled": true
    }
  ],
  "devices": [
    {
      "id": "heater_1",
      "name": "RIMS Heater",
      "type": "heater",
      "pin": 17,
      "enabled": true,
      "linked_sensor_id": "temp_mash"
    }
  ]
}
```

#### POST /equipment/sensor
Add a new sensor.

**Request Body:**
```json
{
  "id": "temp_mash",
  "name": "Mash Tun",
  "nickname": "Primary Mash",
  "type": "temperature",
  "pin": 4,
  "address": "28-000000000001",
  "enabled": true
}
```

**Response:**
```json
{
  "sensor_id": "temp_mash",
  "success": true
}
```

#### POST /equipment/device
Add a new controllable device.

**Request Body:**
```json
{
  "id": "heater_1",
  "name": "RIMS Heater",
  "type": "heater",
  "pin": 17,
  "linked_sensor_id": "temp_mash",
  "enabled": true
}
```

**Response:**
```json
{
  "device_id": "heater_1",
  "success": true
}
```

### Hardware Control

#### POST /hardware/{device_id}/control
Control a hardware device.

**Parameters:**
- `device_id`: Device identifier

**Request Body:**
```json
{
  "action": "on",
  "value": null
}
```

**Response:**
```json
{
  "device_id": "heater_1",
  "action": "on",
  "success": true
}
```

### Timer Management

#### POST /timers
Set a brewing timer.

**Request Body:**
```json
{
  "id": "mash_timer",
  "name": "Mash Timer",
  "duration_minutes": 60,
  "start_immediately": true
}
```

**Response:**
```json
{
  "timer_id": "mash_timer",
  "success": true
}
```

#### GET /timers
Get all timers.

**Response:**
```json
{
  "timers": [
    {
      "id": "mash_timer",
      "name": "Mash Timer",
      "duration_minutes": 60,
      "active": true,
      "remaining_seconds": 3540,
      "expired": false
    }
  ]
}
```

### Alert Management

#### POST /alerts/temperature
Set temperature alerting thresholds.

**Request Body:**
```json
{
  "id": "temp_alert_1",
  "sensor_id": "temp_mash",
  "min_threshold": 60.0,
  "max_threshold": 75.0,
  "enabled": true
}
```

**Response:**
```json
{
  "alert_id": "temp_alert_1",
  "success": true
}
```

### Temperature Control

#### POST /temperature/set
Set target temperature for a device.

**Request Body:**
```json
{
  "temperature": 67.0,
  "device_id": "heater_1"
}
```

**Response:**
```json
{
  "device_id": "heater_1",
  "target_temperature": 67.0,
  "success": true
}
```

#### POST /temperature/stop
Stop temperature control for a specific device or all devices.

**Request Body (optional for specific device):**
```json
{
  "device_id": "heater_1"
}
```

**Response:**
```json
{
  "device_id": "heater_1",
  "success": true
}
```

Or for all:
```json
{
  "success": true
}
```

### System Control

#### POST /system/shutdown
Shutdown the brewing system safely.

#### POST /system/restart
Restart the brewing system.

## Error Responses
All endpoints may return error responses in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

Common error codes:
- `INVALID_REQUEST`: Malformed request
- `NOT_FOUND`: Resource not found
- `SYSTEM_BUSY`: System is currently in use
- `HARDWARE_ERROR`: Hardware malfunction detected
- `SAFETY_VIOLATION`: Operation would violate safety constraints

## WebSocket Support (Future)
Real-time updates will be available via WebSocket connection to `/ws/status`

**Message Format:**
```json
{
  "type": "status_update",
  "data": {
    "temperature": 68.5,
    "status": "brewing"
  },
  "timestamp": "2023-10-01T14:30:00Z"
}
```

## Rate Limiting
- 100 requests per minute per IP
- Burst limit: 20 requests

## Versioning
API versioning follows semantic versioning. Breaking changes will increment the major version number in the URL path.