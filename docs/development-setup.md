# Der Brauer Development Setup

## Prerequisites

### Hardware Requirements
- Raspberry Pi 3 Model B or newer (Pi 4 recommended)
- MicroSD card (32GB minimum)
- Power supply (5V, 3A for Pi 4)
- Ethernet cable or WiFi adapter
- Sensors and actuators for brewing (temperature sensors, relays, etc.)

### Software Requirements
- Raspberry Pi OS (64-bit recommended)
- Python 3.9 or later
- Git
- Virtual environment tools

## Installation Steps

### 1. Raspberry Pi OS Setup
```bash
# Download Raspberry Pi Imager from raspberrypi.com
# Flash Raspberry Pi OS to SD card
# Enable SSH and WiFi in imager settings
# Boot Pi and connect via SSH
```

### 2. System Update
```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Required Packages
```bash
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y python3-rpi.gpio python3-smbus i2c-tools
```

### 4. Clone Repository
```bash
git clone https://github.com/therealbbake/der-brauer.git
cd der-brauer
```

### 5. Virtual Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `fastapi` - Modern async web framework
- `uvicorn` - ASGI server for FastAPI
- `jinja2` - Template engine for HTML rendering
- `pydantic` - Data validation and serialization
- `python-multipart` - Form data handling

**Optional Dependencies (for Raspberry Pi):**
- `RPi.GPIO` - GPIO control (installs automatically on Pi)

## Development Environment

### Local Development (Non-Pi)
For development on non-Raspberry Pi machines:

```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Mock GPIO for testing
pip install RPi.GPIO-stubs
```

### IDE Setup
- Visual Studio Code recommended
- Install Python extension
- Configure interpreter to use virtual environment
- Enable linting and formatting

### Testing
```bash
# Run unit tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run integration tests (on Pi hardware)
python -m pytest tests/integration/
```

## Configuration

### Environment Variables
Create `.env` file in project root:
```bash
# Database
DATABASE_URL=sqlite:///brewing.db

# GPIO Pins (adjust for your setup)
TEMP_SENSOR_PIN=4
HEATER_RELAY_PIN=17
PUMP_RELAY_PIN=27

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/brewing.log
```

### Hardware Configuration
- Map GPIO pins to specific functions
- Configure sensor addresses (I2C)
- Set up safety parameters (max temperatures, etc.)

## Building and Deployment

### Development Build
```bash
python setup.py develop
```

### Production Deployment
```bash
# Install as system service
sudo cp scripts/der-brauer.service /etc/systemd/system/
sudo systemctl enable der-brauer
sudo systemctl start der-brauer
```

### Docker (Future)
```bash
# Build container
docker build -t der-brauer .

# Run container
docker run -d --privileged der-brauer
```

## Debugging

### Logs
```bash
# View application logs
journalctl -u der-brauer -f

# View system logs
dmesg | grep gpio
```

### GPIO Testing
```bash
# Test GPIO pins
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); GPIO.output(17, GPIO.HIGH)"
```

### Network Debugging
```bash
# Check network interfaces
ip addr show

# Test API endpoint
curl http://localhost:8000/status
```

## Troubleshooting

### Common Issues
1. **GPIO Permission Denied**: Run as root or add user to gpio group
   ```bash
   sudo usermod -a -G gpio $USER
   ```

2. **I2C Not Working**: Enable I2C interface
   ```bash
   sudo raspi-config
   # Interface Options > I2C > Enable
   ```

3. **SPI Not Working**: Enable SPI interface
   ```bash
   sudo raspi-config
   # Interface Options > SPI > Enable
   ```

### Performance Optimization
- Use Python optimizations (PyPy if compatible)
- Optimize GPIO operations
- Use asynchronous programming for I/O
- Monitor CPU and memory usage

## Contributing
See [CONTRIBUTING.md](contributing.md) for development guidelines.