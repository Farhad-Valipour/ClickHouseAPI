# Contributing to ClickHouse OHLCV API

Thank you for your interest in contributing! 🎉

---

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** and description
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version, etc.)
- **Logs** if applicable

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- API Version: [e.g., 1.0.0]

## Additional Context
Any other relevant information
```

### Suggesting Features

Feature suggestions are welcome! Please include:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Examples**: Code examples if applicable

### Pull Requests

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass
6. **Update** documentation
7. **Commit** with clear messages
8. **Push** to your fork
9. **Open** a pull request

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional but recommended)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/clickhouse-ohlcv-api.git
cd clickhouse-ohlcv-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env

# Start database
docker-compose up -d clickhouse

# Run tests
pytest
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style
- **Type hints**: Required for all functions
- **Imports**: Organized by standard library, third-party, local

### Code Formatting

We use **Black** for code formatting:

```bash
# Check formatting
black --check .

# Apply formatting
black .
```

### Linting

We use **Flake8** for linting:

```bash
flake8 app/ tests/
```

### Type Checking

We use **MyPy** for type checking:

```bash
mypy app/
```

### Example Code Style

```python
"""
Module docstring explaining purpose.

This module provides...
"""

from typing import Optional, List
from datetime import datetime

from app.core.exceptions import ValidationError


def process_data(
    data: List[dict],
    limit: int = 1000,
    offset: int = 0
) -> Optional[List[dict]]:
    """
    Process data with pagination.
    
    Args:
        data: List of data records
        limit: Maximum records to return
        offset: Number of records to skip
        
    Returns:
        Processed data or None if empty
        
    Raises:
        ValidationError: If limit is invalid
        
    Example:
        >>> data = [{"id": 1}, {"id": 2}]
        >>> result = process_data(data, limit=10)
    """
    if limit <= 0:
        raise ValidationError("Limit must be positive")
    
    start = offset
    end = offset + limit
    
    return data[start:end] if data else None
```

---

## Testing Guidelines

### Writing Tests

- **Test file naming**: `test_*.py`
- **Test function naming**: `test_*`
- **Use fixtures**: Defined in `conftest.py`
- **Coverage target**: >80%

### Test Structure

```python
def test_feature_success():
    """Test successful case."""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected


def test_feature_error():
    """Test error case."""
    with pytest.raises(ExpectedError):
        function(invalid_input)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_health.py::test_basic_health_check

# Run verbose
pytest -v
```

---

## Commit Messages

We use **Conventional Commits** format:

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructure without feature change
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commit messages
feat(api): add pagination support to OHLCV endpoint
fix(db): handle connection timeout properly
docs(readme): update installation instructions
test(health): add tests for readiness check

# Bad commit messages
Update stuff
Fixed bug
Changes
asdf
```

---

## Pull Request Process

### Before Submitting

1. ✅ Code is formatted with Black
2. ✅ All tests pass
3. ✅ New tests added for new features
4. ✅ Documentation updated
5. ✅ Commit messages follow convention
6. ✅ No merge conflicts with main

### PR Template

When opening a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Describe tests that verify your changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] All tests pass locally
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Code review** by maintainers
3. **Address feedback** if requested
4. **Approval** by at least one maintainer
5. **Merge** by maintainer

---

## Documentation

### When to Update Docs

- Adding new features
- Changing API behavior
- Adding configuration options
- Fixing significant bugs

### Documentation Files

- `README.md`: Project overview
- `docs/API.md`: API reference
- `docs/EXAMPLES.md`: Usage examples
- `docs/DEVELOPMENT.md`: Development guide
- Code docstrings: All public functions

### Docstring Format

Use Google style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed. Can span multiple lines
    and include additional context.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg2 is negative
        
    Example:
        >>> result = function("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## Adding New Features

### Feature Development Workflow

1. **Discuss** feature in an issue first
2. **Get approval** from maintainers
3. **Create branch** from `main`
4. **Implement** feature with tests
5. **Document** the feature
6. **Submit PR** following guidelines

### Feature Checklist

- [ ] Feature discussed in issue
- [ ] Implementation complete
- [ ] Tests added (unit + integration)
- [ ] Documentation updated
- [ ] Examples added
- [ ] No breaking changes (or properly documented)
- [ ] Performance considered
- [ ] Security considered

---

## Bug Fixes

### Bug Fix Workflow

1. **Reproduce** the bug
2. **Write test** that fails (demonstrates bug)
3. **Fix** the bug
4. **Verify** test now passes
5. **Add regression test** if needed
6. **Submit PR**

### Bug Fix Checklist

- [ ] Bug reproduced
- [ ] Test added that fails
- [ ] Bug fixed
- [ ] Test passes
- [ ] No side effects
- [ ] Documentation updated if needed

---

## Release Process

(For maintainers)

### Version Numbering

We use **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

1. Update version in `app/__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run all tests
5. Build and test Docker image
6. Create git tag
7. Push to GitHub
8. Create GitHub release
9. Publish documentation

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and features
- **GitHub Discussions**: Questions and ideas
- **Pull Requests**: Code contributions

### Getting Help

- Read the documentation
- Search existing issues
- Ask in discussions
- Be patient and respectful

---

## Recognition

Contributors are recognized in:

- `README.md` contributors section
- GitHub contributors page
- Release notes

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

Feel free to ask questions in:
- GitHub Discussions
- Issue comments
- Pull request comments

Thank you for contributing! 🙏
