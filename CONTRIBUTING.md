# Contributing to Crispex

Thank you for your interest in contributing to Crispex! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/crispex.git
   cd crispex
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation:**
   ```bash
   pytest tests/
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clear, documented code
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Update docstrings

### 3. Add Tests

All new features and bug fixes should include tests:

```python
# tests/test_your_feature.py
import pytest
from crispex.your_module import your_function

def test_your_feature():
    """Test description"""
    result = your_function(input_data)
    assert result == expected_output
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=crispex --cov-report=term-missing

# Run specific test file
pytest tests/test_your_feature.py -v
```

### 5. Check Code Style

```bash
# Format code with black
black crispex/ tests/

# Check with flake8
flake8 crispex/ tests/

# Type checking with mypy (optional)
mypy crispex/
```

### 6. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: Brief description

Detailed explanation of what changed and why.
Fixes #123"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/examples if applicable

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Line length: 100 characters (configured in setup.cfg)
- Use type hints for function signatures
- Write docstrings for all public functions/classes

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input is provided

    Examples:
        >>> function_name("test", 5)
        True
    """
    pass
```

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

## Testing Guidelines

### Test Structure

```python
def test_feature_behavior():
    """Test should do one thing clearly"""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Include integration tests for workflows

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

## Documentation

### Updating Documentation

When adding features:
- Update README.md if user-facing
- Add docstrings to new functions/classes
- Update examples if API changes

### Building Docs (Future)

```bash
# When documentation system is added
cd docs
make html
```

## Types of Contributions

### Bug Reports

When filing a bug report, include:
- Python version
- Crispex version
- Operating system
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

For feature requests, describe:
- Use case and motivation
- Proposed solution
- Alternative approaches considered
- Breaking changes (if any)

### Code Contributions

We welcome:
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

## Priority Areas

Current priorities for contributions:

1. **Full Azimuth model integration** - Replace heuristic predictor
2. **Genome-wide off-target search** - FM-index implementation
3. **Additional test coverage** - Especially CLI and integration tests
4. **Performance optimization** - Speed up guide extraction
5. **Additional Cas variants** - SaCas9, Cas12a support

## Review Process

1. All PRs require at least one review
2. All tests must pass
3. Code coverage should not decrease
4. Documentation must be updated

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Build and publish to PyPI

## Communication

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## Code of Conduct

Be respectful and inclusive. We're all here to advance CRISPR research and make guide design accessible to everyone.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or start a discussion if you have questions!

---

Thank you for contributing to Crispex!
