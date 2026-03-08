# Contributing to Der Brauer

Thank you for your interest in contributing to Der Brauer! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:
- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/der-brauer.git
cd der-brauer
```

### 2. Set Up Development Environment
Follow the [development setup guide](development-setup.md) to configure your environment.

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 4. Make Changes
- Write clear, concise commit messages
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 5. Test Your Changes
```bash
# Run unit tests
python -m pytest

# Run integration tests (on Raspberry Pi)
python -m pytest tests/integration/

# Test on actual hardware when possible
```

### 6. Submit a Pull Request
- Ensure your branch is up to date with main
- Provide a clear description of changes
- Reference any related issues
- Request review from maintainers

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length under 88 characters (Black formatter default)

### Commit Messages
Use conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

Examples:
```
feat(api): add temperature monitoring endpoint
fix(gpio): resolve heater relay timing issue
docs(readme): update installation instructions
```

### Testing
- Write unit tests for all new code
- Aim for >80% code coverage
- Include integration tests for hardware interactions
- Test on actual Raspberry Pi hardware when possible

### Documentation
- Update relevant documentation for any changes
- Add docstrings to new functions
- Keep API documentation current
- Update changelog for user-facing changes

## Project Structure
```
der-brauer/
├── src/                    # Source code
│   ├── controller/         # Main control logic
│   ├── hardware/           # Hardware abstraction layer
│   ├── api/                # REST API endpoints
│   └── models/             # Data models
├── tests/                  # Test files
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── scripts/                # Deployment and utility scripts
└── requirements.txt        # Python dependencies
```

## Hardware Testing
For contributions involving hardware:
1. Test on supported Raspberry Pi models
2. Document any hardware requirements
3. Include safety considerations
4. Provide wiring diagrams if applicable

## Issue Reporting
When reporting bugs:
- Use the issue template
- Include Raspberry Pi model and OS version
- Provide error logs and stack traces
- Describe steps to reproduce
- Include hardware setup details

## Feature Requests
For new features:
- Check existing issues first
- Use the feature request template
- Describe the problem and proposed solution
- Consider backward compatibility

## Review Process
- All PRs require review before merging
- Maintainers may request changes
- CI/CD must pass for all changes
- Squash commits when merging to main

## Licensing
By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition
Contributors will be acknowledged in:
- CHANGELOG.md for significant contributions
- Repository contributors list
- Release notes

## Questions?
- Check existing documentation first
- Search existing issues and discussions
- Create a new discussion for questions
- Contact maintainers for sensitive matters

Thank you for contributing to Der Brauer!