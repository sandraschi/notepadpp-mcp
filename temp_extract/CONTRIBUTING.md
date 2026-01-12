# Contributing to Notepad++ MCP Server

Thank you for your interest in contributing to the Notepad++ MCP Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## Getting Started

### Prerequisites

- **Python 3.10+** installed
- **Windows 10/11** (required for full functionality)
- **Notepad++ 8.0+** installed
- **Git** for version control

### Quick Start

```bash
# Clone the repository
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp

# Set up development environment
python dev.py install-dev

# Run tests to verify setup
python -m pytest src/notepadpp_mcp/tests/

# Run demonstration
python demonstration_test.py
```

## Development Setup

### Environment Setup

1. **Clone and Install**:
   ```bash
   git clone https://github.com/sandraschi/notepadpp-mcp.git
   cd notepadpp-mcp
   pip install -e .[dev]
   ```

2. **Verify Installation**:
   ```bash
   python -c "import notepadpp_mcp; print('Installation successful')"
   ```

### Development Tools

- **Testing**: pytest with coverage reporting
- **Linting**: black, isort, mypy
- **Building**: hatch for packaging
- **CI/CD**: GitHub Actions

## Development Workflow

### Branching Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: Feature branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical fixes for production

### Commit Convention

We follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing changes
- `chore`: Maintenance tasks

**Examples**:
```
feat(tools): add new linting functionality
fix(windows-api): resolve handle leak in controller
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Write tests first (TDD approach)
   - Follow coding standards
   - Update documentation

3. **Run Quality Checks**:
   ```bash
   # Format code
   black src/
   isort src/

   # Run tests
   python -m pytest src/notepadpp_mcp/tests/ --cov=src/notepadpp_mcp

   # Type checking
   mypy src/notepadpp_mcp
   ```

4. **Update Documentation**:
   - Update CHANGELOG.md
   - Update docstrings
   - Update README if needed

5. **Create Pull Request**:
   - Use PR template
   - Reference related issues
   - Request review from maintainers

## Coding Standards

### Python Style

- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting
- **mypy**: Type checking with strict settings

### Code Quality

- **No print() statements**: Use structured logging instead
- **Comprehensive error handling**: All functions must handle errors gracefully
- **Input validation**: Validate all user inputs
- **Documentation**: All public functions must have docstrings

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Files**: `snake_case.py`

### Logging Standards

```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information messages")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical errors")
```

## Testing

### Test Structure

```
src/notepadpp_mcp/tests/
├── conftest.py          # Test configuration and fixtures
├── test_server.py      # Main server tests
└── test_*.py           # Additional test files
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/notepadpp_mcp

# Run specific test
python -m pytest src/notepadpp_mcp/tests/test_server.py::TestClass::test_method
```

### Writing Tests

- **Test naming**: `test_descriptive_name`
- **Arrange-Act-Assert**: Follow this pattern
- **Mock external dependencies**: Use pytest fixtures for mocking
- **Test edge cases**: Include error conditions and boundary values

### Test Coverage

- **Target**: >80% code coverage
- **Critical paths**: 100% coverage for core functionality
- **Report**: Coverage reports generated automatically in CI

## Documentation

### Code Documentation

- **Docstrings**: All public functions and classes
- **Type hints**: Use typing module for all function parameters and return values
- **Comments**: Explain complex logic, not obvious code

### User Documentation

- **README.md**: Installation and usage instructions
- **CHANGELOG.md**: Version history and changes
- **API Documentation**: Generated from docstrings

### Updating Documentation

```bash
# Update CHANGELOG.md
# Add entries under [Unreleased] section
# Move to version section when releasing

# Update README.md
# Keep installation instructions current
# Update feature lists and examples
```

## Submitting Changes

### Before Submitting

1. **Self-review**: Check your code against the standards
2. **Test thoroughly**: All tests pass, no regressions
3. **Documentation updated**: CHANGELOG, README, docstrings
4. **Commits squashed**: Clean, logical commit history

### Pull Request Checklist

- [ ] Tests pass on all supported Python versions
- [ ] Code follows style guidelines (black, isort)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No print() statements remain
- [ ] New features have comprehensive tests

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Peer Review**: At least one maintainer review required
3. **Approval**: Maintainers approve and merge
4. **Deployment**: Changes deployed through automated process

## Reporting Issues

### Bug Reports

Use the bug report template and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Logs and error messages

### Feature Requests

Use the feature request template and include:

- Clear description of the proposed feature
- Use case and benefits
- Implementation ideas (optional)
- Alternative solutions considered

### Questions and Support

- **GitHub Discussions**: General questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Check existing docs first

## Recognition

Contributors will be:
- Listed in CHANGELOG.md for significant contributions
- Acknowledged in release notes
- Added to contributors list for major contributions

Thank you for contributing to Notepad++ MCP Server! 🎉

---

**Last Updated**: September 30, 2025
