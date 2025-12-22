### `docs/DEVELOPMENT.md`
# CryptoCore Development Guide

## Table of Contents
1. [Development Environment](#development-environment)
2. [Project Structure](#project-structure)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Testing Strategy](#testing-strategy)
5. [Adding New Features](#adding-new-features)
6. [Debugging](#debugging)
7. [Performance Optimization](#performance-optimization)
8. [Security Considerations](#security-considerations)
9. [Release Process](#release-process)
10. [Contributing](#contributing)

## Development Environment

### Prerequisites
- Python 3.6 or higher
- pip and virtualenv
- Git

### Setup Development Environment

#### 1. Clone Repository

git clone https://github.com/yourusername/cryptocore.git
cd cryptocore
2. Create Virtual Environment

# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
3. Install Dependencies

# Development dependencies
pip install -e .[dev]

# Or manually
pip install -e .
pip install pytest pytest-cov pylint black mypy
pip install -r requirements.txt
4. Verify Setup

# Run tests
python run_tests.py

# Check code style
pylint src/
Project Structure

cryptocore/
├── src/                          
│   ├── cryptocore.py             
│   ├── cli_parser.py              
│   ├── file_io.py               
│   ├── csprng.py                  
│   ├── modes/                     
│   │   ├── __init__.py
│   │   ├── base.py               
│   │   ├── ecb.py               
│   │   ├── cbc.py                 
│   │   ├── cfb.py                
│   │   ├── ofb.py                 
│   │   ├── ctr.py                 
│   │   ├── gcm.py                 
│   │   └── encrypt_then_mac.py    
│   ├── hash/                      
│   │   ├── __init__.py
│   │   ├── sha256.py              
│   │   ├── sha3_256.py            
│   │   └── utils.py               
│   ├── mac/                      
│   │   ├── __init__.py
│   │   ├── hmac.py            
│   │   ├── cmac.py               
│   │   └── utils.py               
│   └── kdf/                       
│       ├── __init__.py
│       ├── pbkdf2.py             
│       └── hkdf.py                
├── tests/                         
│   ├── unit/                      
│   │   ├── test_aes.py
│   │   ├── test_hash.py
│   │   ├── test_hmac.py
│   │   ├── test_kdf.py
│   │   └── test_csprng.py
│   ├── integration/            
│   │   ├── test_modes.py
│   │   ├── test_cli.py
│   │   └── test_end_to_end.py
│   ├── vectors/                 
│   │   ├── nist_aes.json
│   │   ├── nist_gcm.json
│   │   ├── nist_sha256.json
│   │   ├── nist_sha3_256.json
│   │   ├── rfc_4231_hmac.json
│   │   └── rfc_6070_pbkdf2.json
│   └── run_tests.py              
├── docs/                        
│   ├── API.md
│   ├── USERGUIDE.md
│   ├── DEVELOPMENT.md
│   └── examples/                  
├── examples/                   
├── scripts/                       
├── requirements.txt             
├── setup.py                      
├── setup.cfg                      
├── pyproject.toml                
├── .pylintrc                   
├── .gitignore                    
├── LICENSE                       
└── README.md                     
Module Dependencies
python
# High-level view of module dependencies
cryptocore.py → cli_parser.py, modes/, hash/, mac/, kdf/, csprng.py, file_io.py
modes/ → Crypto.Cipher.AES (pycryptodome)
hash/ → (pure Python implementations)
mac/ → hash/
kdf/ → mac/
Code Style Guidelines
Python Style
Follow PEP 8
Use 4 spaces per indentation level

Maximum line length: 79 characters

Use descriptive variable names

Write docstrings for all public functions

Example
python
def encrypt_data(key: bytes, plaintext: bytes, mode: str = 'cbc') -> bytes:
    """
    Encrypt data using specified mode.
    
    Args:
        key: 16-byte encryption key
        plaintext: Data to encrypt
        mode: Encryption mode ('cbc', 'gcm', etc.)
    
    Returns:
        Encrypted ciphertext
        
    Raises:
        ValueError: If key length is invalid
        AuthenticationError: If authentication fails (GCM)
    """
    # Implementation...
Documentation Standards
Function Docstrings
python
def function_name(param1: type, param2: type) -> return_type:
    """
    One-line description.
    
    Extended description explaining purpose, algorithm,
    and important details.
    
    Args:
        param1: Description with constraints
        param2: Description with units if applicable
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this exception is raised
        
    Examples:
        >>> function_name(value1, value2)
        expected_result
        
    Notes:
        Additional information, implementation details,
        or security considerations.
    """
Class Docstrings
python
class ClassName:
    """
    Class purpose and responsibility.
    
    Attributes:
        attr1: Description of attribute
        attr2: Description with type hint
        
    Methods:
        method1: Brief description
        method2: Brief description
        
    Example:
        >>> obj = ClassName()
        >>> obj.method1()
    """
    
    def __init__(self, param: type):
        """
        Initialize the class.
        
        Args:
            param: Description
        """
Type Hints
Use Python type hints for better code clarity and tooling support.

python
from typing import Optional, Tuple, List, Union

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
Security Considerations in Code
1. Clear Sensitive Data
python
def process_password(password: str) -> bytes:
    """
    Process password and clear from memory.
    """
    try:
        # Convert to bytes
        password_bytes = password.encode('utf-8')
        result = process_password_bytes(password_bytes)
        
        # Clear sensitive data
        password_bytes = b'\x00' * len(password_bytes)
        password = '\x00' * len(password)
        
        return result
    finally:
        # Ensure cleanup
        password_bytes = b'\x00' * len(password_bytes)
        password = '\x00' * len(password)
2. Constant-Time Operations
python
def verify_hmac(computed: bytes, expected: bytes) -> bool:
    """
    Constant-time HMAC verification.
    
    Prevents timing attacks by always comparing
    all bytes regardless of mismatch position.
    """
    if len(computed) != len(expected):
        return False
    
    result = 0
    for x, y in zip(computed, expected):
        result |= x ^ y
    
    return result == 0
Testing Strategy
Test Categories
1. Unit Tests
Test individual functions and classes

Mock dependencies when necessary

Achieve >90% code coverage

Location: tests/unit/

2. Integration Tests
Test module interactions

Test CLI commands end-to-end

Test file I/O operations

Location: tests/integration/

3. Known-Answer Tests (KATs)
Test against NIST/RFC test vectors

Ensure algorithm correctness

Test edge cases

Location: tests/vectors/

4. Performance Tests
Benchmark critical operations

Test memory usage

Test with large files

Location: tests/performance/

Writing Tests
Example Unit Test
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
    
    def test_incremental_hashing(self):
        """Test incremental hash updates."""
        hasher = SHA256()
        hasher.update(b"Hello, ")
        hasher.update(b"World!")
        result1 = hasher.hexdigest()
        
        result2 = SHA256().hash_hex(b"Hello, World!")
        
        self.assertEqual(result1, result2)
    
    def test_large_data(self):
        """Test with large data."""
        large_data = b"A" * (1024 * 1024)  # 1MB
        hasher = SHA256()
        result = hasher.hash_hex(large_data)
        
        self.assertEqual(len(result), 64)  # 32 bytes = 64 hex chars
        self.assertTrue(all(c in '0123456789abcdef' for c in result))
Example Integration Test
python
import unittest
import tempfile
import os
import subprocess

class TestCLIEncryption(unittest.TestCase):
    """Test CLI encryption/decryption."""
    
    def test_roundtrip_cbc(self):
        """Test CBC encryption and decryption."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            original = b"Test data for encryption roundtrip"
            f.write(original)
            input_file = f.name
        
        encrypted = input_file + '.enc'
        decrypted = input_file + '.dec'
        
        try:
            # Encrypt
            subprocess.run([
                "cryptocore", "--algorithm", "aes", "--mode", "cbc",
                "--encrypt", "--key", "0" * 32,
                "--input", input_file, "--output", encrypted
            ], check=True)
            
            # Decrypt
            subprocess.run([
                "cryptocore", "--algorithm", "aes", "--mode", "cbc",
                "--decrypt", "--key", "0" * 32,
                "--input", encrypted, "--output", decrypted
            ], check=True)
            
            # Verify
            with open(decrypted, 'rb') as f:
                result = f.read()
            
            self.assertEqual(original, result)
            
        finally:
            for f in [input_file, encrypted, decrypted]:
                if os.path.exists(f):
                    os.remove(f)
Running Tests
Run All Tests
bash
python run_tests.py
Run Specific Test Categories
bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Specific test file
python -m pytest tests/unit/test_aes.py -v

# With coverage report
python -m pytest --cov=src tests/ -v
Test Coverage
bash
# Generate coverage report
python -m pytest --cov=src --cov-report=html tests/

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
Adding New Features
Development Workflow
1. Create Feature Branch
bash
git checkout -b feature/new-algorithm
2. Implement Feature
Add new module or extend existing ones

Follow code style guidelines

Write comprehensive docstrings

Add type hints

3. Write Tests
Unit tests for new functionality

Integration tests for CLI integration

Update known-answer tests if applicable

4. Update Documentation
Update API.md with new functions

Update USERGUIDE.md with usage examples

Update DEVELOPMENT.md if architecture changes

5. Code Review
Self-review using pylint and mypy

Peer review if available

Security review for cryptographic code

6. Merge and Release
bash
git checkout main
git merge --no-ff feature/new-algorithm
git tag -a v8.1.0 -m "Add new-algorithm feature"
git push origin main --tags
Example: Adding New Hash Algorithm
1. Create Module
python
# src/hash/sha512.py
"""
SHA-512 implementation (NIST FIPS 180-4).
"""

class SHA512:
    """SHA-512 hash function."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset hash state."""
        # Initial hash values
        self.h = [
            0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
            0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
            0x510e527fade682d1, 0x9b05688c2b3e6c1f,
            0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
        ]
        self.buffer = bytearray(128)
        self.buffer_len = 0
        self.total_len = 0
    
    def update(self, data: bytes):
        """Update hash with more data."""
        # Implementation...
    
    def digest(self) -> bytes:
        """Return raw hash bytes."""
        # Implementation...
    
    def hexdigest(self) -> str:
        """Return hex-encoded hash."""
        return self.digest().hex()
    
    def hash_hex(self, data: bytes) -> str:
        """One-shot hash computation."""
        self.reset()
        self.update(data)
        return self.hexdigest()
2. Update Factory Function
python
# src/hash/__init__.py
from .sha512 import SHA512

def create_hash(algorithm: str):
    """Create hash instance."""
    algorithm = algorithm.lower()
    
    if algorithm == 'sha256':
        return SHA256()
    elif algorithm == 'sha3-256':
        return SHA3_256()
    elif algorithm == 'sha512':  # NEW
        return SHA512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
3. Add CLI Support
python
# src/cli_parser.py
def _validate_hash_args(args):
    """Validate hash arguments."""
    valid_algorithms = ['sha256', 'sha3-256', 'sha512']  # Updated
    # ...
4. Write Tests
python
# tests/unit/test_hash.py
class TestSHA512(unittest.TestCase):
    """Test SHA-512 implementation."""
    
    def test_empty_string(self):
        hasher = SHA512()
        result = hasher.hash_hex(b"")
        expected = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        self.assertEqual(result, expected)
Debugging
Common Debugging Techniques
1. Logging
python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def encrypt_data(key: bytes, data: bytes):
    """Encrypt data with debug logging."""
    logger.debug("Encrypting %d bytes with key: %s...", 
                 len(data), key[:8].hex())
    
    try:
        # Encryption logic
        result = encrypt_impl(key, data)
        logger.debug("Encryption successful")
        return result
    except Exception as e:
        logger.error("Encryption failed: %s", e, exc_info=True)
        raise
2. Interactive Debugging
python
# Add breakpoint for debugging
import pdb

def complex_function():
    # Complex logic
    pdb.set_trace()  # Debugger will stop here
    # Continue execution
3. Test Debugging
python
# Run tests with debug output
python -m pytest tests/unit/test_aes.py -v -s

# Run with pdb on failure
python -m pytest tests/unit/test_aes.py --pdb
Debugging Cryptographic Issues
1. Compare with Known Values
python
def debug_hash():
    """Debug hash function issues."""
    from cryptocore.hash import SHA256
    import hashlib
    
    data = b"test"
    
    # Our implementation
    our_hash = SHA256().hash_hex(data)
    print(f"Our hash: {our_hash}")
    
    # Reference implementation
    ref_hash = hashlib.sha256(data).hexdigest()
    print(f"Reference: {ref_hash}")
    
    if our_hash != ref_hash:
        print("MISMATCH!")
        # Debug step-by-step
2. Debug Encryption
python
def debug_encryption():
    """Debug encryption issues."""
    from cryptocore.modes import create_mode
    from Crypto.Cipher import AES
    
    key = b'0' * 16
    iv = b'0' * 16
    data = b'Hello World!'
    
    # Our implementation
    our_cipher = create_mode('cbc', key, iv)
    our_result = our_cipher.encrypt(data)
    
    # Reference
    ref_cipher = AES.new(key, AES.MODE_CBC, iv)
    # Note: Need to handle padding differences
Performance Optimization
Profiling
1. CPU Profiling
python
import cProfile
import pstats
from cryptocore.hash import SHA256

def profile_hash():
    """Profile hash function."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    hasher = SHA256()
    for i in range(1000):
        hasher.update(b"test" * 1000)
        hasher.hexdigest()
        hasher.reset()
    
    profiler.disable()
    
    # Print results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
2. Memory Profiling
python
from memory_profiler import profile

@profile
def process_large_file():
    """Profile memory usage."""
    with open('large_file.bin', 'rb') as f:
        hasher = SHA256()
        while chunk := f.read(8192):
            hasher.update(chunk)
        return hasher.hexdigest()
Optimization Techniques
1. Use Local Variables
python
def optimized_function(data: bytes):
    """Optimized version with local variables."""
    # Instead of self.constant multiple times
    k = self.constants
    h = self.hash_state
    
    for i in range(len(data)):
        # Use local variables in loop
        byte = data[i]
        # Optimized operations...
2. Precompute Constants
python
class OptimizedHash:
    """Hash with precomputed constants."""
    
    # Precomputed constants
    CONSTANTS = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        # ... more constants
    ]
    
    def process_block(self, block):
        """Process block with precomputed constants."""
        for i in range(64):
            # Use precomputed constant
            constant = self.CONSTANTS[i]
            # Optimization...
3. Use Built-in Functions
python
def optimized_xor(a: bytes, b: bytes) -> bytes:
    """Optimized XOR operation."""
    # Use bytes comprehension instead of loop
    return bytes(x ^ y for x, y in zip(a, b))
Security Considerations
Security Review Checklist
Code Security
No hardcoded keys or passwords

Sensitive data cleared from memory

Input validation on all parameters

Bounds checking for all buffers

Integer overflow prevention

Error handling without information leakage

Cryptographic Security
Use cryptographically secure RNG

Implement constant-time comparisons

No reuse of nonces/IVs with same key

Proper key derivation parameters

Authentication before decryption

Protection against side-channel attacks

Operational Security
Secure default settings

Clear security warnings in documentation

Deprecation of insecure algorithms

Secure file handling

Proper permission handling

Security Testing
1. Fuzz Testing
python
import random
import string

def fuzz_test_hash():
    """Fuzz test hash function."""
    hasher = SHA256()
    
    for _ in range(10000):
        # Generate random input
        length = random.randint(0, 10000)
        data = bytes(random.randint(0, 255) for _ in range(length))
        
        try:
            # Should not crash
            result = hasher.hash_hex(data)
            assert len(result) == 64
            assert all(c in '0123456789abcdef' for c in result)
        except Exception as e:
            print(f"Failed with data length {length}: {e}")
            raise
2. Timing Attack Tests
python
import time

def test_constant_time_verification():
    """Test that verification is constant-time."""
    correct = b"correct_mac"
    wrong = b"wrong_mac____"
    
    times_correct = []
    times_wrong = []
    
    for _ in range(1000):
        start = time.perf_counter_ns()
        verify_hmac(correct, correct)
        times_correct.append(time.perf_counter_ns() - start)
        
        start = time.perf_counter_ns()
        verify_hmac(correct, wrong)
        times_wrong.append(time.perf_counter_ns() - start)
    
    avg_correct = sum(times_correct) / len(times_correct)
    avg_wrong = sum(times_wrong) / len(times_wrong)
    
    # Should be within 10%
    ratio = avg_wrong / avg_correct
    assert 0.9 <= ratio <= 1.1, f"Timing difference: {ratio}"
Release Process
Versioning
Semantic Versioning
MAJOR: Incompatible API changes

MINOR: New features (backwards compatible)

PATCH: Bug fixes (backwards compatible)

Example: v8.1.3 = Major 8, Minor 1, Patch 3

Release Checklist
Pre-Release
All tests pass

Code coverage meets target (>90%)

Documentation updated

Security review completed

Performance benchmarks recorded

CHANGELOG.md updated

Release Steps
Update version in setup.py

Update CHANGELOG.md

Create release branch

Run full test suite

Build distribution packages

Tag release in Git

Push to package repository

Update documentation

Post-Release
Verify installation from PyPI (if applicable)

Update website/documentation

Announce release

Monitor for issues

Automated Release Script
python
#!/usr/bin/env python3
"""
Automated release script.
"""
import subprocess
import sys
import re

def run_command(cmd):
    """Run command and check return code."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def release_new_version(version):
    """Release new version."""
    # Update version in setup.py
    with open('setup.py', 'r') as f:
        content = f.read()
    
    content = re.sub(
        r'version="[^"]+"',
        f'version="{version}"',
        content
    )
    
    with open('setup.py', 'w') as f:
        f.write(content)
    
    # Run tests
    run_command("python run_tests.py")
    
    # Create tag
    run_command(f'git tag -a v{version} -m "Release v{version}"')
    run_command(f'git push origin v{version}')
    
    # Build and upload (if configured)
    # run_command("python setup.py sdist bdist_wheel")
    # run_command("twine upload dist/*")
    
    print(f"Successfully released v{version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python release.py <version>")
        sys.exit(1)
    
    release_new_version(sys.argv[1])
Contributing
Contribution Guidelines
Getting Started
Fork the repository

Create feature branch

Make changes

Write tests

Update documentation

Submit pull request

Code Standards
Follow PEP 8 style guide

Write comprehensive docstrings

Add type hints for new functions

Write tests for new features

Update relevant documentation

Pull Request Process
Ensure all tests pass

Update CHANGELOG.md

Add documentation

Request review from maintainers

Address review comments

Merge after approval

Code of Conduct
Expected Behavior
Use welcoming and inclusive language

Respect different viewpoints and experiences

Accept constructive criticism gracefully

Focus on what's best for the community

Unacceptable Behavior
Harassment or discrimination

Trolling or insulting comments

Publishing others' private information

Any unethical or unprofessional conduct

Recognition
Contributors will be acknowledged in:

CONTRIBUTORS.md file

Release notes

Project documentation

Getting Help
Open an issue for bugs or questions

Check existing documentation

Contact maintainers for security issues

Additional Resources
Learning Resources
NIST Cryptographic Standards

RFC Repository

Cryptography Engineering Book

Tools
OpenSSL - Reference implementation

Wireshark - Network analysis

Burp Suite - Security testing

Communities
Crypto StackExchange

Python Crypto Developers

OWASP - Security community