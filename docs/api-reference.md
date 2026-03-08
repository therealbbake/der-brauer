# Der Brauer API Reference

## Overview
The Der Brauer API provides REST endpoints for controlling and monitoring the brewing process. All endpoints return JSON responses.

Base URL: `http://localhost:8000/api/v1`

## Authentication
Currently no authentication required (local network only). Future versions will include API key authentication.

## Endpoints

### Status and Monitoring

#### GET /status
Get current brewing system status.

**Response:**
```json
{
  "status": "idle|brewing|mashing|boiling|fermenting",
  "temperature": 68.5,
  "target_temperature": 67.0,
  "pump_status": "on|off",
  "heater_status": "on|off",
  "current_recipe": "Pale Ale v1.0",
  "stage_start_time": "2023-10-01T14:30:00Z",
  "estimated_completion": "2023-10-01T18:30:00Z"
}
```

#### GET /sensors
Get real-time sensor data.

**Response:**
```json
{
  "temperature_sensors": [
    {
      "id": "mash_tun",
      "value": 68.5,
      "unit": "celsius",
      "timestamp": "2023-10-01T14:30:00Z"
    },
    {
      "id": "ambient",
      "value": 22.0,
      "unit": "celsius",
      "timestamp": "2023-10-01T14:30:00Z"
    }
  ],
  "pressure_sensors": [],
  "flow_sensors": []
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

### System Control

#### POST /system/shutdown
Shutdown the brewing system safely.

#### POST /system/restart
Restart the brewing system.

#### GET /system/config
Get system configuration.

#### PUT /system/config
Update system configuration.

**Request Body:**
```json
{
  "gpio_pins": {
    "heater": 17,
    "pump": 27,
    "temp_sensor": 4
  },
  "safety_limits": {
    "max_temperature": 100.0,
    "min_temperature": 0.0
  }
}
```

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