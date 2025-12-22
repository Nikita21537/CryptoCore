### `docs/USERGUIDE.md`

# CryptoCore User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Encryption & Decryption](#encryption--decryption)
4. [Hash Functions](#hash-functions)
5. [Message Authentication Codes](#message-authentication-codes)
6. [Key Derivation](#key-derivation)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Comparison with Other Tools](#comparison-with-other-tools)
10. [Quick Reference](#quick-reference)

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Installation Methods

#### Method 1: From Source (Recommended)

# Clone the repository
git clone https://github.com/yourusername/cryptocore.git
cd cryptocore

# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
Method 2: From PyPI (Future Release)

pip install cryptocore
Method 3: Manual Installation

# Download the package
# Extract and navigate to directory
python setup.py install
Platform-Specific Notes
Linux/macOS

# Ensure Python 3.6+ is installed
python3 --version

# Install with pip3
pip3 install -e .
Windows
powershell
# Using PowerShell
.\venv\Scripts\Activate.ps1
pip install -e .

# Or using Command Prompt
venv\Scripts\activate.bat
pip install -e .
Verification

# Check installation
cryptocore --help

# Expected output showing available commands
Quick Start
1. Encrypt a File

# Encrypt with auto-generated key
cryptocore --algorithm aes --mode cbc --encrypt \
  --input secret.txt \
  --output secret.enc
Save the displayed key! You'll need it for decryption.

2. Decrypt the File

cryptocore --algorithm aes --mode cbc --decrypt \
  --key YOUR_SAVED_KEY_HERE \
  --input secret.enc \
  --output secret_decrypted.txt
3. Verify Integrity

# Check that files match
diff secret.txt secret_decrypted.txt
Encryption & Decryption
Available Algorithms and Modes
Mode	Description	IV Required	Authentication	Padding
ECB	Electronic Codebook	No	No	PKCS#7
CBC	Cipher Block Chaining	Yes	No	PKCS#7
CFB	Cipher Feedback	Yes	No	None
OFB	Output Feedback	Yes	No	None
CTR	Counter	Yes	No	None
GCM	Galois/Counter Mode	Yes	Yes	None
ETM	Encrypt-then-MAC	Yes	Yes	PKCS#7
Basic Encryption
With Auto-generated Key

cryptocore --algorithm aes --mode MODE --encrypt \
  --input plaintext.txt \
  --output ciphertext.bin
With Specific Key

cryptocore --algorithm aes --mode cbc --encrypt \
  --key 00112233445566778899aabbccddeeff \
  --input data.txt \
  --output data.enc
Basic Decryption
With IV in File

cryptocore --algorithm aes --mode cbc --decrypt \
  --key YOUR_KEY \
  --input encrypted.bin \
  --output decrypted.txt
With Explicit IV

cryptocore --algorithm aes --mode cbc --decrypt \
  --key YOUR_KEY \
  --iv IV_HEX_STRING \
  --input ciphertext_only.bin \
  --output plaintext.txt
Authenticated Encryption (GCM)
Encryption with AAD

cryptocore --algorithm aes --mode gcm --encrypt \
  --key 00112233445566778899aabbccddeeff \
  --input database.sql \
  --output database.enc \
  --aad "database_version_3.2"
Decryption with Verification

cryptocore --algorithm aes --mode gcm --decrypt \
  --key 00112233445566778899aabbccddeeff \
  --input database.enc \
  --output database_decrypted.sql \
  --aad "database_version_3.2"
Important: If authentication fails (wrong AAD or tampered data), no output file is created.

File Formats
IV-Containing Modes (CBC, CFB, OFB, CTR)

[16-byte IV][Ciphertext bytes]
GCM Mode

[12-byte nonce][Ciphertext][16-byte authentication tag]
Encrypt-then-MAC Mode

[16-byte IV (optional)][Ciphertext][32-byte HMAC tag]
Hash Functions
Basic Hashing
File Hash

# SHA-256
cryptocore dgst --algorithm sha256 --input file.iso

# SHA3-256
cryptocore dgst --algorithm sha3-256 --input file.iso --output hash.txt
STDIN Hash

# Hash piped data
cat file.txt | cryptocore dgst --algorithm sha256 --input -

# Hash command output
ls -la | cryptocore dgst --algorithm sha256 --input -
Hash Verification
Create Hash File

cryptocore dgst --algorithm sha256 --input original.iso --output original.sha256
Verify Later

cryptocore dgst --algorithm sha256 --input downloaded.iso | diff - original.sha256
Message Authentication Codes
HMAC Generation
Basic HMAC

cryptocore dgst --algorithm sha256 --hmac \
  --key 00112233445566778899aabbccddeeff \
  --input message.txt
Save HMAC to File

cryptocore dgst --algorithm sha256 --hmac \
  --key YOUR_KEY \
  --input document.pdf \
  --output document.pdf.hmac
HMAC Verification
Verify File Integrity

cryptocore dgst --algorithm sha256 --hmac \
  --key YOUR_KEY \
  --input received.pdf \
  --verify expected.hmac
AES-CMAC (Bonus Feature)

cryptocore dgst --algorithm sha256 --cmac \
  --key 16_BYTE_KEY_HEX \
  --input data.bin
Key Derivation
PBKDF2 Key Derivation
With Specified Salt

cryptocore derive --password "MySecurePassword123!" \
  --salt 1234567890abcdef1234567890abcdef \
  --iterations 100000 \
  --length 32
Output Format: KEY_HEX SALT_HEX

With Auto-generated Salt
bash
cryptocore derive --password "ApplicationSecret" \
  --iterations 500000 \
  --length 16 \
  --output derived_key.txt
Raw Binary Output
bash
cryptocore derive --password "test" \
  --salt 1234567890abcdef \
  --iterations 10000 \
  --length 32 \
  --raw \
  --output key.bin
RFC 6070 Test Vectors
Test Vector 1
bash
cryptocore derive --password "password" \
  --salt 73616c74 \
  --iterations 1 \
  --length 20
# Expected: 0c60c80f961f0e71f3a9b524af6012062fe037a6
Test Vector 2
bash
cryptocore derive --password "password" \
  --salt 73616c74 \
  --iterations 2 \
  --length 20
# Expected: ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957
Security Best Practices
Key Management
Do:
Use cryptographically secure random keys

Store keys in secure key management systems

Rotate keys regularly (every 90 days for high security)

Use different keys for different purposes

Clear keys from memory after use

Don't:
Hardcode keys in source code

Store keys alongside encrypted data

Use weak keys (all zeros, patterns, etc.)

Reuse keys across different applications

Mode Selection
Recommended:
Confidentiality + Integrity: GCM mode

Encryption with separate integrity: Encrypt-then-MAC

Legacy compatibility: CBC mode with HMAC

Avoid:
ECB mode (reveals patterns)

Unauthenticated modes for sensitive data

Password Security
Strong Password Guidelines:
Minimum 12 characters

Mix of uppercase, lowercase, numbers, symbols

Avoid dictionary words and patterns

Use password managers

Key Derivation Settings:
Minimum 100,000 iterations for PBKDF2

16+ byte random salt per password

32+ byte derived keys

File Security
Encryption:
Always use authenticated encryption for important files

Include metadata as AAD (authenticated but not encrypted)

Verify files haven't been tampered with before use

Integrity Checking:
Use HMAC for files transferred over networks

Store hash/MAC separately from the file

Verify signatures from trusted sources

Troubleshooting
Common Errors
"Error: Invalid hexadecimal key"
Problem: Key is not a valid hex string.

Solution:


# Ensure key is 32 hex characters (16 bytes)
cryptocore --key 00112233445566778899aabbccddeeff ...
"Authentication failed"
Problem: GCM/ETM authentication failed.

Causes:

Wrong AAD (Associated Authenticated Data)

Tampered ciphertext

Corrupted file

Solution:

Verify AAD matches encryption AAD

Check file integrity

Ensure using correct key

"File too short for IV"
Problem: Encrypted file is corrupted or incomplete.

Solution:

Verify file size matches expected

Check for transmission errors

Re-download or restore from backup

"Weak key detected"
Warning: Key appears to be weak.

Solution:

Generate a new random key

Don't use sequential or repeated bytes

Performance Issues
Slow Key Derivation
Problem: PBKDF2 with high iterations is slow.

Solution:

Use appropriate iteration count for your use case

Consider hardware acceleration for production

Cache derived keys when appropriate

Large File Processing
Problem: Processing very large files (>1GB).

Solution:

Tool uses streaming, no memory issues

Be patient, encryption takes time

Consider hardware acceleration

Interoperability Issues
OpenSSL Compatibility
Problem: Files encrypted with CryptoCore don't decrypt with OpenSSL.

Solution:


# Extract IV and ciphertext
dd if=crypto.bin of=iv.bin bs=16 count=1
dd if=crypto.bin of=ciphertext.bin bs=16 skip=1

# Decrypt with OpenSSL
openssl enc -aes-128-cbc -d \
  -K YOUR_KEY_HEX \
  -iv $(xxd -p iv.bin | tr -d '\n') \
  -in ciphertext.bin \
  -out decrypted.txt
Comparison with Other Tools
vs OpenSSL
Feature	CryptoCore	OpenSSL
Implementation	From scratch	Mature library
Authenticated Encryption	GCM, Encrypt-then-MAC	GCM, CCM, OCB
Hash Functions	SHA-256, SHA3-256 (scratch)	Many algorithms
Key Derivation	PBKDF2 from scratch	PBKDF2, scrypt, argon2
Ease of Use	Simple CLI	Complex options
Learning Value	Educational	Production
vs GPG (GNU Privacy Guard)
Feature	CryptoCore	GPG
Purpose	Symmetric encryption	Public-key encryption
Key Management	Simple keys	Complex keyrings
Authentication	Built-in	Separate signatures
File Format	Custom formats	OpenPGP standard
Use Case	File encryption	Email, messaging
When to Use CryptoCore
Educational purposes - Learn cryptography implementation

Simple file encryption - Quick symmetric encryption

Testing - Compare with other implementations

Custom workflows - Integrate into Python scripts

When to Use Other Tools
Production systems - Use OpenSSL or libsodium

Public-key cryptography - Use GPG or OpenSSL

Standard compliance - Use NIST/FIPS validated libraries

Quick Reference
Command Cheat Sheet
Encryption/Decryption

# Encrypt
cryptocore --algorithm aes --mode MODE --encrypt --key KEY --input IN --output OUT

# Decrypt  
cryptocore --algorithm aes --mode MODE --decrypt --key KEY --input IN --output OUT

# With IV
cryptocore ... --iv IV_HEX

# With AAD (GCM/ETM)
cryptocore ... --aad AAD_HEX
Hash/MAC

# Hash
cryptocore dgst --algorithm ALGO --input FILE

# HMAC
cryptocore dgst --algorithm ALGO --hmac --key KEY --input FILE

# Verify
cryptocore dgst --algorithm ALGO --hmac --key KEY --input FILE --verify MAC_FILE
Key Derivation

# Derive key
cryptocore derive --password PASS --salt SALT --iterations N --length L

# Save to file
cryptocore derive ... --output FILE

# Raw binary
cryptocore derive ... --raw
Common Parameters
Parameter	Values	Description
--algorithm	aes, sha256, sha3-256	Cryptographic algorithm
--mode	ecb, cbc, cfb, ofb, ctr, gcm, etm	Encryption mode
--key	32 hex chars (16 bytes)	Encryption/MAC key
--iv	32 hex chars (16 bytes)	Initialization vector
--aad	Hex string	Associated authenticated data
--iterations	Integer ≥1	PBKDF2 iteration count
--length	Integer ≥1	Key length in bytes
Exit Codes
Code	Meaning
0	Success
1	General error
2	Invalid arguments
3	Authentication failure
4	File I/O error
Getting Help
Documentation
docs/API.md - Complete API reference

docs/DEVELOPMENT.md - Developer guide

examples/ - Code examples

Testing

# Run all tests
python run_tests.py

# Run specific tests
python -m pytest tests/unit/test_aes.py -v
Support
Check troubleshooting section above

Review examples in examples/ directory

Consult API documentation for detailed usage