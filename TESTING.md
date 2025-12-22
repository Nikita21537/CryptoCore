# CryptoCore Testing Documentation

## Overview

This document describes the testing procedures for CryptoCore, including
cryptographic validation and statistical randomness tests.

## Unit Tests

Run the complete test suite:


python -m pytest tests/ -v
Or run specific test modules:


# Test CSPRNG functionality
python -m pytest tests/test_csprng.py -v

# Test encryption modes
python -m pytest tests/test_modes.py -v
CSPRNG Testing
1. Basic Randomness Tests
The test suite includes basic statistical checks:

Uniqueness Test: Generates 1000 AES keys and verifies all are unique

Distribution Test: Verifies approximately 50% of bits are set to 1

Weak Key Detection: Tests detection of common weak key patterns

2. NIST Statistical Test Suite
For rigorous randomness testing, use the NIST Statistical Test Suite.

Preparation
Install NIST STS:

Download from NIST website

Or use Python version: pip install nist-sts

Generate test data:


# Generate 10MB of random data using CryptoCore's CSPRNG
python -c "
from src.csprng import generate_random_bytes
data = generate_random_bytes(10_000_000)
with open('random_data.bin', 'wb') as f:
    f.write(data)
print('Generated 10MB of random data in random_data.bin')
"
Running NIST Tests
Using Python NIST-STS:

bash
# Install the Python wrapper
pip install nist-sts

# Run tests
python -m nist_sts.run random_data.bin
Using Original C Implementation:

Compile the NIST STS from source

Run the assessment tool:


./assess 10000000  # 10 million bits = 1.25MB minimum
Follow the interactive prompts to specify your test file.

Expected Results
For a cryptographically secure RNG:

Most tests should pass (p-value ≥ 0.01)

A small number of marginal failures is statistically expected

Widespread failures indicate problems with the RNG

Interoperability Testing
With OpenSSL
Verify that CryptoCore can encrypt and OpenSSL can decrypt (and vice versa):


# 1. Encrypt with CryptoCore, decrypt with OpenSSL
cryptocore --algorithm aes --mode cbc --encrypt \
           --input plain.txt --output crypto_cipher.bin

# Extract IV (first 16 bytes) and ciphertext
dd if=crypto_cipher.bin of=iv.bin bs=16 count=1
dd if=crypto_cipher.bin of=cipher_only.bin bs=16 skip=1

# Get key from CryptoCore output and use it with OpenSSL
openssl enc -aes-128-cbc -d \
            -K YOUR_GENERATED_KEY_HEX \
            -iv $(xxd -p iv.bin | tr -d '\n') \
            -in cipher_only.bin \
            -out openssl_decrypted.txt

# Compare with original
diff plain.txt openssl_decrypted.txt
Round-Trip Testing
Basic round-trip test within CryptoCore:

# Create test file
echo "Test data" > test.txt

# Encrypt (with auto-generated key)
cryptocore --algorithm aes --mode ctr --encrypt \
           --input test.txt --output test.enc

# Decrypt (using the key printed during encryption)
cryptocore --algorithm aes --mode ctr --decrypt \
           --key YOUR_GENERATED_KEY \
           --input test.enc --output test.dec

# Verify
diff test.txt test.dec
Performance Testing
Generate timing information for different operations:


# Time key generation
time python -c "from src.csprng import generate_aes_key; generate_aes_key()"

# Time encryption of different file sizes
for size in 1 10 100 1000; do
    dd if=/dev/zero of=test_${size}kb.bin bs=1024 count=$size
    time cryptocore --algorithm aes --mode cbc --encrypt \
                    --input test_${size}kb.bin --output test_${size}kb.enc
done
Security Notes
Key Security:

Generated keys are only printed to stdout, never written to disk

Users must securely store generated keys

Weak key detection warns about potentially insecure keys

Randomness Source:

Uses os.urandom() which is cryptographically secure

On Linux/macOS: reads from /dev/urandom

On Windows: uses CryptGenRandom API

IV Generation:

Always uses secure random IVs for encryption

IVs are prepended to ciphertext files

For decryption, IVs can be read from file or provided via CLI

Test Coverage
Current test coverage includes:

✓ CSPRNG functionality

✓ All encryption modes (ECB, CBC, CFB, OFB, CTR)

✓ Key generation and weak key detection

✓ File I/O with IV handling

✓ CLI argument parsing

✓ Basic interoperability with OpenSSL
# CryptoCore Testing Documentation

## Hash Function Testing

### NIST Test Vectors
Both SHA-256 and SHA3-256 implementations pass NIST test vectors:


# SHA-256 NIST vectors
test_vectors = [
    ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    # ... more vectors
]
## 4. Обновленный 

# CryptoCore Testing Documentation

## Hash Function Testing

### NIST Test Vectors
Both SHA-256 and SHA3-256 implementations pass NIST test vectors:

```python
# SHA-256 NIST vectors
test_vectors = [
    ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    # ... more vectors
]
Avalanche Effect Test
Changing one bit in input changes approximately 50% of output bits:

bash
python -c "
from src.hash import SHA256
import binascii

data1 = b'Hello, world!'
data2 = b'Hello, world?'

hash1 = SHA256().hash_hex(data1)
hash2 = SHA256().hash_hex(data2)

# Count differing bits
bin1 = bin(int(hash1, 16))[2:].zfill(256)
bin2 = bin(int(hash2, 16))[2:].zfill(256)
diff = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))

print(f'Bits changed: {diff}/256 ({diff/256*100:.1f}%)')
"
Large File Test
Test with files larger than 1GB:

python
# Generate and test large file
import tempfile
import os
from src.hash import hash_file

# Create 1.1GB test file
with tempfile.NamedTemporaryFile(delete=False) as f:
    # Write in chunks to avoid memory issues
    chunk = b'A' * 1024 * 1024  # 1MB chunks
    for _ in range(1100):  # 1.1GB total
        f.write(chunk)
    
    hash_value = hash_file(f.name, 'sha256')
    print(f"SHA-256 of 1.1GB file: {hash_value}")
Running Tests
Complete Test Suite

python -m pytest tests/ -v --tb=short
Individual Test Modules

# Hash function tests
python -m pytest tests/test_hash.py::TestSHA256 -v
python -m pytest tests/test_hash.py::TestSHA3_256 -v
python -m pytest tests/test_hash.py::TestNISTVectors -v

# CLI tests
python -m pytest tests/test_hash.py::TestCLIHash -v
Performance Testing

# Time hash computation
time cryptocore dgst --algorithm sha256 --input large_file.iso

# Compare with system tools
time sha256sum large_file.iso
Test Coverage
✓ NIST test vectors for SHA-256 and SHA3-256

✓ Empty input and various length inputs

✓ Incremental hashing vs one-shot hashing

✓ Avalanche effect verification

✓ Large file handling (streaming)

✓ CLI interface correctness

✓ Interoperability with system tools

✓ Error handling for missing files