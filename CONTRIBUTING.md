# Contributing to CryptoCore

Thank you for your interest in contributing to CryptoCore! This document provides guidelines and instructions for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Security Issues](#security-issues)
9. [Community](#community)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Git
- pip (Python package installer)

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/cryptocore.git
   cd cryptocore
Create a virtual environment:

bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\Activate.ps1
Install development dependencies:

bash
pip install -e .[dev]
Run tests to verify setup:

bash
python run_tests.py
Finding Issues to Work On
Check the Issues page

Look for issues labeled good-first-issue or help-wanted

Consider improving documentation or adding tests

Review TODO comments in the codebase

Development Workflow
1. Create a Feature Branch
Always create a new branch for your work:

bash
git checkout -b feature/description-of-feature
Branch naming conventions:

feature/ - New features or enhancements

bugfix/ - Bug fixes

docs/ - Documentation improvements

test/ - Test additions or improvements

refactor/ - Code refactoring

2. Make Your Changes
Follow the Code Standards below.

3. Write Tests
Add tests for new functionality or update existing tests.

4. Update Documentation
Update relevant documentation:

API documentation in docs/API.md

User guide in docs/USERGUIDE.md

Development guide in docs/DEVELOPMENT.md

README.md if necessary

5. Run Tests and Checks
Before submitting, run:

bash
# Run all tests
python run_tests.py

# Check code style
pylint src/

# Run type checking
mypy src/

# Check formatting
black --check src/ tests/
6. Commit Your Changes
Use descriptive commit messages:

bash
git add .
git commit -m "Add feature: brief description

Detailed explanation of changes:
- What changed
- Why it changed
- Any breaking changes

Fixes #123"
Commit message format:

First line: summary (50 chars or less)

Blank line

Detailed description

Reference issues

7. Push to Your Fork
bash
git push origin feature/description-of-feature
8. Create a Pull Request
Go to the original repository on GitHub

Click "New Pull Request"

Select your branch

Fill in the PR template

Submit for review

Code Standards
Python Style Guide
We follow PEP 8 with some modifications:

Line length: 100 characters

Indentation: 4 spaces

Naming:

Functions/Methods/Variables: snake_case

Classes: PascalCase

Constants: UPPER_SNAKE_CASE

Documentation
All public functions, classes, and modules must have docstrings:

python
def function_name(param1: type, param2: type) -> return_type:
    """
    One-line description.
    
    Extended description if needed.
    
    Args:
        param1: Description with constraints
        param2: Description with units
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When and why raised
        
    Example:
        >>> function_name(value1, value2)
        expected_result
    """
Type Hints
Use Python type hints for all function signatures:

python
from typing import Optional, List, Tuple

def process_data(
    data: bytes,
    key: Optional[bytes] = None,
    options: List[str] = None
) -> Tuple[bool, bytes]:
    """
    Process data with optional key.
    """
    if options is None:
        options = []
    # Implementation...
Security Considerations
For cryptographic code:

Clear sensitive data from memory after use

Use constant-time operations for comparisons

Validate all inputs thoroughly

Never log sensitive information

Follow cryptographic best practices

Example:

python
def verify_mac(computed: bytes, expected: bytes) -> bool:
    """
    Constant-time MAC verification.
    """
    if len(computed) != len(expected):
        return False
    
    result = 0
    for x, y in zip(computed, expected):
        result |= x ^ y
    
    return result == 0
Import Organization
Organize imports in this order:

Standard library imports

Third-party imports

Local application imports

With blank lines between groups:

python
import os
import sys
from typing import Optional

from Crypto.Cipher import AES

from . import utils
from .exceptions import CryptoCoreError
Testing
Test Categories
Unit Tests (tests/unit/):

Test individual functions and classes

Mock external dependencies

Aim for >90% code coverage

Integration Tests (tests/integration/):

Test module interactions

Test CLI commands end-to-end

Test file I/O operations

Known-Answer Tests (tests/vectors/):

Test against NIST/RFC test vectors

Ensure algorithm correctness

Performance Tests:

Benchmark critical operations

Test memory usage with large files

Writing Tests
Example test structure:

python
import unittest
from cryptocore.hash import SHA256

class TestSHA256(unittest.TestCase):
    """Test SHA-256 implementation."""
    
    def test_empty_string(self):
        """Test hash of empty string."""
        hasher = SHA256()
        result = hasher.hash_hex(b"")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(result, expected)
    
    def test_avalanche_effect(self):
        """Test avalanche effect."""
        data1 = b"Hello, world!"
        data2 = b"Hello, world?"
        
        hash1 = SHA256().hash_hex(data1)
        hash2 = SHA256().hash_hex(data2)
        
        self.assertNotEqual(hash1, hash2)
Running Tests
bash
# Run all tests
python run_tests.py

# Run specific test category
python run_tests.py --unit
python run_tests.py --integration

# Run with pytest directly
python -m pytest tests/unit/test_hash.py -v

# Run with coverage
python -m pytest --cov=src tests/ --cov-report=html
Documentation
Documentation Structure
docs/API.md - Complete API reference

docs/USERGUIDE.md - User guide with examples

docs/DEVELOPMENT.md - Developer guide (this file)

examples/ - Code examples

README.md - Project overview

Writing Documentation
Be clear and concise

Include examples

Document edge cases

Update when code changes

Use proper Markdown formatting

Example:

markdown
## Function Name

### Description
Brief description of what the function does.

### Parameters
- `param1` (type): Description
- `param2` (type): Description with constraints

### Returns
Description of return value.

### Example
result = function_name(value1, value2)
print(result)
Notes
Additional information or warnings.

text

## Pull Request Process

### PR Requirements

1. **Tests must pass**
2. **Code coverage maintained** (≥90%)
3. **Documentation updated**
4. **Code follows style guide**
5. **Security review completed**

### PR Template

When creating a PR, fill in this template:
Description
Brief description of changes.

Type of Change
Bug fix

New feature

Breaking change

Documentation update

Test addition

Testing
Unit tests added/updated

Integration tests added/updated

All tests pass

Documentation
API documentation updated

User guide updated

Development guide updated

Security
Security review completed

No sensitive data exposed

Input validation added

Related Issues
Fixes #123
Related to #456

Additional Notes
Any additional information.

text

### Review Process

1. **Automated checks** (CI) run automatically
2. **Maintainer review** within 2 business days
3. **Address feedback** promptly
4. **Merge after approval**

## Security Issues

### Reporting Security Issues

**Do not report security issues in public issues or pull requests.**

Instead, please email security@example.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Review Checklist

When contributing cryptographic code:

- [ ] No hardcoded keys or passwords
- [ ] Sensitive data cleared from memory
- [ ] Constant-time operations where needed
- [ ] Input validation on all parameters
- [ ] Protection against side-channel attacks
- [ ] Follows cryptographic best practices

## Community

### Getting Help

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and discussions
- **Email**: For security issues only

### Recognition

Contributors will be acknowledged in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [NIST Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [RFC Repository](https://www.rfc-editor.org/)

Thank you for contributing to CryptoCore! 🎉