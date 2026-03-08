# Der Brauer Architecture

## System Overview
Der Brauer follows a modular architecture designed for reliability, maintainability, and scalability on Raspberry Pi hardware.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Dashboard     │ │ Manual Control  │ │ Equipment Setup │ │
│  │   (Monitoring)  │ │   (Control)     │ │   (Config)      │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   REST API      │ │   Brew          │ │   Hardware       │ │
│  │   Endpoints     │ │   Controller    │ │   Manager       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Hardware Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Sensors       │ │   Actuators     │ │   GPIO/I2C      │ │
│  │   (Temp, Press) │ │   (Heaters,     │ │   Interface     │ │
│  │                 │ │    Pumps)       │ │                 │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Control Service
- Core brewing logic and state management
- Handles brewing recipes and process automation
- Manages sensor data collection and actuator control
- Provides REST API for external communication
- Continuous background monitoring for timers, alerts, and multi-device temperature control with hysteresis

### 2. Hardware Controllers
- GPIO pin management for digital I/O
- I2C/SPI communication with sensors
- PWM control for actuators (heaters, pumps)
- Safety interlocks and error handling

### 3. Sensor Integration
- Temperature sensors (DS18B20, thermocouples)
- Pressure sensors
- Flow meters
- pH sensors (future)

### 4. Data Storage
- SQLite database for local data persistence
- Configuration files for settings
- Log files for debugging and monitoring

### 5. User Interface (Planned)
- Web dashboard for monitoring and control
- Mobile app compatibility
- Recipe editor and management

## Communication Protocols
- Internal: Python inter-process communication
- External: HTTP/REST API
- Hardware: GPIO, I2C, SPI, 1-Wire

## Data Flow
1. Sensors → Hardware Controllers → Control Service
2. Control Service processes data and makes decisions
3. Control Service → Hardware Controllers → Actuators
4. Control Service → API responses → Web Interface

## Design Principles
- **Modularity**: Components can be developed and tested independently
- **Reliability**: Fail-safe mechanisms for critical brewing processes
- **Scalability**: Architecture supports expansion to multiple RPi units
- **Maintainability**: Clear separation of concerns and documentation

## Deployment
- Single Raspberry Pi deployment for home use
- Potential multi-unit setup for larger operations
- Docker containerization for easier deployment (future)

## Security Considerations
- Local network operation (no internet exposure by default)
- API authentication for remote access
- Hardware safety features (thermal cutoffs, etc.)

## Future Extensions
- Cloud integration for remote monitoring
- Machine learning for process optimization
- Integration with brewing equipment manufacturers