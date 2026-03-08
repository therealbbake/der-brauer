# Der Brauer Project Overview

## Purpose
Der Brauer is a Raspberry Pi-based service designed to control and monitor the various stages of the brewing process. It provides automated control for temperature, timing, and other parameters critical to beer brewing.

## Features
- Automated brewing stage management
- Temperature monitoring and control (Celsius/Fahrenheit)
- W1 sensor auto-discovery and configuration
- Sensor nickname system for easy identification
- Device-sensor linking for temperature-controlled equipment
- Recipe management (planned)
- Real-time status updates and monitoring
- Web-based interface with responsive design
- Manual control panel for direct hardware operation
- Timer management for brewing stages
- Temperature alerting with configurable thresholds
- Equipment setup and configuration interface

## Technology Stack
- Hardware: Raspberry Pi 3B+ or newer
- Operating System: Raspberry Pi OS (64-bit)
- Programming Language: Python 3.9+
- Web Framework: FastAPI (async)
- Template Engine: Jinja2
- Frontend: Bootstrap 5 + Vanilla JavaScript
- Database: SQLite (planned)
- Communication: REST API, GPIO, I2C, W1

## Project Status
- Phase: MVP Development
- Current State: Core architecture implemented with functional web interface

## Key Components
- **FastAPI Backend**: Async REST API with comprehensive endpoints
- **Hardware Manager**: GPIO control, sensor reading, W1 discovery
- **Brew Controller**: Process logic, timers, temperature alerts
- **Web Interface**: Dashboard, manual control, equipment setup
- **Sensor Integration**: DS18B20 temperature sensors with auto-discovery
- **Device Control**: Relay control for heaters, pumps, valves
- **Data Management**: Configuration persistence and logging

## Target Users
- Homebrewers looking to automate their brewing process
- Small-scale craft breweries
- Educational institutions teaching brewing technology

## Repository Structure
```
der-brauer/
├── README.md
├── docs/
│   ├── goals.md
│   ├── project-overview.md (this file)
│   └── ...
├── src/ (planned)
├── tests/ (planned)
└── scripts/ (planned)