# Dependencies Management

This document explains the dependency management for the trading system.

## Single Requirements File

The project uses a **single `requirements.txt` file** that includes all dependencies:
- Core trading system dependencies
- Testing framework
- Development tools
- Optional utilities

## Installation

### Quick Start
```bash
pip install -r requirements.txt
```

### Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Using Makefile
```bash
make install
```

## Dependency Categories

### Core Dependencies
- **pandas** (>=2.0.0): Data manipulation and analysis
- **numpy** (>=1.20.0): Numerical computing
- **yfinance** (>=0.2.0): Yahoo Finance market data

### Testing Framework
- **pytest** (>=6.0.0): Main testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-xdist**: Parallel test execution
- **pytest-html**: HTML test reports
- **coverage**: Coverage measurement

### Development Tools
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **pre-commit**: Pre-commit hooks

### Optional Test Utilities
- **pytest-benchmark**: Performance testing
- **factory-boy**: Test data generation
- **Faker**: Fake data generation
- **freezegun**: Time mocking for tests

## Customizing Dependencies

### Minimal Installation
If you want only core dependencies, create a minimal requirements file:

```bash
# requirements-minimal.txt
pandas>=2.0.0,<3.0.0
numpy>=1.20.0,<3.0.0
yfinance>=0.2.0,<1.0.0
```

### Production Installation
For production environments, comment out development tools:

```bash
pip install -r requirements.txt --no-deps
# Then install only core dependencies manually
```

### Development Installation
The default `requirements.txt` includes all development tools.

## Version Management

### Version Constraints
- **Upper bounds**: Prevent breaking changes (`<3.0.0`)
- **Lower bounds**: Ensure minimum features (`>=2.0.0`)
- **Compatible versions**: Balance stability and features

### Updating Dependencies
```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade pandas

# Regenerate requirements
pip freeze > requirements-new.txt
```

### Security Updates
```bash
# Check for security vulnerabilities
pip-audit

# Update to secure versions
pip install --upgrade package-name
```

## Environment-Specific Requirements

### Development Environment
```bash
# Full installation with all tools
pip install -r requirements.txt
```

### CI/CD Environment
```bash
# Same as development (includes testing tools)
pip install -r requirements.txt
```

### Production Environment
```bash
# Consider creating requirements-prod.txt with only core deps
pip install pandas numpy yfinance
```

## Dependency Resolution

### Common Issues

**1. Version Conflicts**
```bash
# Use pip's dependency resolver
pip install --use-pep517 -r requirements.txt

# Or install with constraints
pip install -r requirements.txt -c constraints.txt
```

**2. Platform-Specific Issues**
```bash
# Create platform-specific requirements
pip freeze --platform linux_x86_64 > requirements-linux.txt
```

**3. Python Version Compatibility**
```bash
# Check compatibility
pip check

# Install for specific Python version
python3.9 -m pip install -r requirements.txt
```

### Best Practices

1. **Pin Major Versions**: Use `>=X.Y.0,<X+1.0.0` format
2. **Regular Updates**: Update dependencies monthly
3. **Security Scanning**: Use `pip-audit` regularly
4. **Lock Files**: Consider using `pip-tools` for lock files
5. **Virtual Environments**: Always use virtual environments

## Alternative Package Managers

### Using pip-tools
```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in file with high-level deps
echo "pandas>=2.0.0" > requirements.in
echo "numpy>=1.20.0" >> requirements.in

# Generate locked requirements.txt
pip-compile requirements.in

# Install from locked file
pip-sync requirements.txt
```

### Using Poetry
```bash
# Initialize poetry project
poetry init

# Add dependencies
poetry add pandas numpy yfinance

# Add dev dependencies
poetry add --group dev pytest black flake8

# Install all dependencies
poetry install
```

### Using Conda
```bash
# Create environment.yml
conda env create -f environment.yml

# Or install from requirements.txt
conda create --name trading-system --file requirements.txt
```

## Troubleshooting

### Installation Issues

**Common Solutions:**
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Clear cache: `pip cache purge`
3. Use `--no-cache-dir` flag
4. Install from source: `pip install --no-binary=package-name`

### Import Errors
```python
# Check installed packages
import sys
print(sys.path)

# Verify package installation
import pandas
print(pandas.__version__)
```

### Version Verification
```bash
# List all installed packages
pip list

# Show specific package info
pip show pandas

# Check for conflicts
pip check
```

## Contributing

When adding new dependencies:

1. **Update requirements.txt** with version constraints
2. **Test installation** in clean environment
3. **Document purpose** in commit message
4. **Consider alternatives** - avoid heavy dependencies
5. **Update CI/CD** if needed

Example:
```bash
# Add new dependency
echo "matplotlib>=3.5.0,<4.0.0  # For plotting functionality" >> requirements.txt

# Test installation
pip install -r requirements.txt

# Update documentation if needed
```