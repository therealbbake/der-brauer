# Changelog

All notable changes to Der Brauer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete FastAPI backend with async architecture
- Hardware management system with GPIO control and sensor reading
- Temperature unit support (Celsius/Fahrenheit) with real-time conversion
- W1 sensor auto-discovery for DS18B20 temperature sensors
- Sensor nickname system for user-friendly identification
- Device-sensor linking for temperature-controlled equipment (Heater/Kettle/Fridge)
- Real-time brewing monitoring dashboard with status display
- Manual control panel for device operation and timer management
- Equipment setup interface with sensor discovery and configuration
- Temperature alerting system with configurable thresholds
- Timer management for brewing stages
- Bootstrap-based responsive web UI with modern styling
- Comprehensive API endpoints for all system functions
- Environment variable configuration support

### Changed
- Enhanced MVP roadmap to focus on core UI components and hardware setup
- Updated goals to include UI dashboard, manual controls, and temperature alerting
- Improved architecture documentation with current system design

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2023-10-01

### Added
- Initial commit with basic repository structure
- README.md with project description
- Basic documentation folder setup
- .gitignore for Python/Raspberry Pi development

### Changed
- N/A

### Fixed
- N/A

---

## Guidelines for Changelog Updates

### Types of Changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Release Process
1. Update version in relevant files (`__init__.py`, `setup.py`, etc.)
2. Move unreleased changes to a new version section
3. Add release date
4. Create git tag
5. Update any deployment scripts
6. Publish to package repository if applicable

### Commit Message Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation only changes
- style: Changes that do not affect the meaning of the code
- refactor: A code change that neither fixes a bug nor adds a feature
- test: Adding missing tests or correcting existing tests
- chore: Changes to the build process or auxiliary tools

Example:
```
feat(api): add temperature monitoring endpoint

Add GET /api/v1/temperature endpoint to retrieve current temperature readings from all sensors.

Closes #42