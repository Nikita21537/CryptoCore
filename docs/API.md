# CryptoCore API Documentation

## Overview

CryptoCore is a cryptographic library and command-line tool providing implementations of:
- AES-128 encryption with multiple modes (ECB, CBC, CFB, OFB, CTR, GCM, Encrypt-then-MAC)
- Hash functions (SHA-256, SHA3-256) from scratch
- Message Authentication Codes (HMAC-SHA256, AES-CMAC)
- Key Derivation Functions (PBKDF2, key hierarchy)
- Cryptographically secure random number generation

## Table of Contents

1. [Core Modules](#core-modules)
2. [AES Encryption](#aes-encryption)
3. [Hash Functions](#hash-functions)
4. [Message Authentication Codes](#message-authentication-codes)
5. [Key Derivation Functions](#key-derivation-functions)
6. [Cryptographically Secure RNG](#cryptographically-secure-rng)
7. [CLI Interface](#cli-interface)
8. [Error Handling](#error-handling)
9. [Security Considerations](#security-considerations)

## Core Modules

### Module: `cryptocore.modes`
Base classes and factories for encryption modes.

#### `create_mode(mode: str, key: bytes, iv: Optional[bytes] = None) -> BaseCipher`
Creates a cipher instance for the specified mode.

**Parameters:**
- `mode` (str): Encryption mode: 'ecb', 'cbc', 'cfb', 'ofb', 'ctr', 'gcm', 'etm'
- `key` (bytes): Encryption key (16 bytes for AES-128)
- `iv` (bytes, optional): Initialization vector (required for some modes)

**Returns:**
- `BaseCipher`: Cipher instance with encrypt() and decrypt() methods

**Raises:**
- `ValueError`: If mode is invalid or key/iv lengths are incorrect

**Example:**
from cryptocore.modes import create_mode

key = os.urandom(16)
iv = os.urandom(16)
cipher = create_mode('cbc', key, iv)

ciphertext = cipher.encrypt(b"Secret message")
plaintext = cipher.decrypt(ciphertext)
Module: cryptocore.file_io
File I/O utilities for cryptographic operations.

read_file_with_iv(filepath: str, has_iv: bool = False) -> Tuple[Optional[bytes], bytes]
Reads a file, optionally extracting IV from the beginning.

Parameters:

filepath (str): Path to the file

has_iv (bool): Whether the file starts with a 16-byte IV

Returns:

Tuple[Optional[bytes], bytes]: (IV or None, data)

Raises:

IOError: If file cannot be read

ValueError: If file is too short to contain IV

Example:

python
from cryptocore.file_io import read_file_with_iv

iv, data = read_file_with_iv('encrypted.bin', has_iv=True)
AES Encryption
Module: cryptocore.modes.ecb
AES-128 ECB mode implementation.

AES_ECB(key: bytes)
ECB mode cipher with PKCS#7 padding.

Parameters:

key (bytes): 16-byte AES key

Methods:

encrypt(plaintext: bytes) -> bytes: Encrypts data with PKCS#7 padding

decrypt(ciphertext: bytes) -> bytes: Decrypts and removes padding

Security Note: ECB mode reveals patterns and should not be used for sensitive data.

Module: cryptocore.modes.cbc
AES-128 CBC mode implementation.

AES_CBC(key: bytes, iv: bytes)
CBC mode cipher with PKCS#7 padding.

Parameters:

key (bytes): 16-byte AES key

iv (bytes): 16-byte initialization vector

Methods:

encrypt(plaintext: bytes) -> bytes: Encrypts with CBC chaining

decrypt(ciphertext: bytes) -> bytes: Decrypts CBC chain

Module: cryptocore.modes.gcm
AES-128 GCM mode implementation (authenticated encryption).

GCM(key: bytes, nonce: Optional[bytes] = None)
Galois/Counter Mode with authentication.

Parameters:

key (bytes): 16-byte AES key

nonce (bytes, optional): 12-byte nonce (auto-generated if None)

Properties:

nonce (bytes): The nonce used for encryption/decryption

Methods:

encrypt(plaintext: bytes, aad: bytes = b"") -> bytes: Encrypts with authentication

decrypt(ciphertext: bytes, aad: bytes = b"") -> bytes: Decrypts and verifies authentication

Raises:

AuthenticationError: If authentication fails (tampered data or wrong AAD)

Security Note: Never reuse a nonce with the same key.

Hash Functions
Module: cryptocore.hash
Hash function implementations from scratch.

SHA256()
SHA-256 hash function (NIST FIPS 180-4).

Methods:

update(data: bytes): Updates hash with more data

digest() -> bytes: Returns raw hash bytes

hexdigest() -> str: Returns hex-encoded hash

hash_hex(data: bytes) -> str: One-shot hash computation

Example:

python
from cryptocore.hash import SHA256

hasher = SHA256()
hasher.update(b"Hello, ")
hasher.update(b"World!")
hash_value = hasher.hexdigest()  # "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
SHA3_256()
SHA3-256 hash function (Keccak sponge, NIST FIPS 202).

Methods: Same as SHA256

Utility Functions
hash_data(data: bytes, algorithm: str = 'sha256') -> bytes: One-shot hash

hash_data_hex(data: bytes, algorithm: str = 'sha256') -> str: One-shot hex hash

hash_file(filepath: str, algorithm: str = 'sha256') -> str: File hash

Message Authentication Codes
Module: cryptocore.mac
MAC implementations.

HMAC(key: bytes, algorithm: str = 'sha256')
HMAC with specified hash function.

Parameters:

key (bytes): MAC key (any length)

algorithm (str): Hash algorithm ('sha256' or 'sha3-256')

Methods:

compute(data: bytes) -> bytes: Computes MAC

compute_hex(data: bytes) -> str: Computes hex MAC

verify(data: bytes, mac: bytes) -> bool: Verifies MAC

HMACStream(key: bytes, algorithm: str = 'sha256')
Streaming HMAC for large files.

Methods:

update(data: bytes): Updates with more data

finalize() -> bytes: Finalizes MAC computation

finalize_hex() -> str: Finalizes as hex

AESCMAC(key: bytes)
AES-CMAC implementation (NIST SP 800-38B).

Parameters:

key (bytes): 16-byte AES key

Methods: Same as HMAC

Key Derivation Functions
Module: cryptocore.kdf
Key derivation functions.

pbkdf2_hmac_sha256(password: Union[str, bytes], salt: Union[str, bytes], iterations: int, dklen: int) -> bytes
PBKDF2 with HMAC-SHA256 (RFC 2898).

Parameters:

password: Password as string or bytes

salt: Salt as string, hex string, or bytes

iterations: Number of iterations (recommended: ≥100,000)

dklen: Desired key length in bytes

Returns:

bytes: Derived key

Example:

python
from cryptocore.kdf import pbkdf2_hmac_sha256

key = pbkdf2_hmac_sha256(
    password="MyPassword123!",
    salt=b"randomsalt",
    iterations=100000,
    dklen=32
)
derive_key(master_key: bytes, context: Union[str, bytes], length: int = 32) -> bytes
Derives subkeys from a master key.

Parameters:

master_key: Master key bytes

context: Context identifier (e.g., "encryption", "authentication")

length: Desired key length

Returns:

bytes: Derived key

Cryptographically Secure RNG
Module: cryptocore.csprng
Cryptographically secure random number generation.

generate_random_bytes(num_bytes: int) -> bytes
Generates cryptographically secure random bytes.

Parameters:

num_bytes: Number of bytes to generate

Returns:

bytes: Random bytes

generate_aes_key() -> bytes
Generates a random 16-byte AES key.

generate_iv() -> bytes
Generates a random 16-byte initialization vector.

generate_salt(length: int = 16) -> bytes
Generates a random salt.

is_key_weak(key: bytes) -> bool
Checks if a key appears weak (all zeros, patterns, etc.).

print_key_info(key: bytes, source: str = "generated") -> None
Prints key information and statistics.

CLI Interface
Module: cryptocore.cli_parser
Command-line argument parsing.

parse_args() -> argparse.Namespace
Parses command-line arguments.

Commands:

enc: Encryption/decryption

dgst: Hash/MAC computation

derive: Key derivation

Module: cryptocore.cryptocore
Main CLI implementation.

main()
Entry point for the CLI tool.

Error Handling
Exception Hierarchy
text
CryptoCoreError
├── EncryptionError
├── AuthenticationError
│   ├── GCMAuthError
│   └── ETMAuthError
├── HashError
├── MacError
├── KDFError
└── CSPRNGError
Error Recovery
Authentication failures: No output file created

Invalid inputs: Clear error messages

File errors: Descriptive IOError messages

Security Considerations
Critical Requirements
Never log or print secret keys (except when explicitly requested)

Use cryptographically secure RNG for all random values

Clear sensitive memory after use

Perform authentication before decryption (GCM, HMAC)

Validate all user inputs

Handle errors securely without leaking sensitive information

Algorithm Recommendations
Encryption: Use GCM or Encrypt-then-MAC

Hashing: SHA-256 or SHA3-256

Key derivation: PBKDF2 with ≥100,000 iterations

MAC: HMAC-SHA256 or AES-CMAC

Key Management
Store keys in secure key management systems

Rotate keys regularly

Use different keys for different purposes (via key hierarchy)

Version Information
Current Version: 8.0.0
Python Compatibility: 3.6+
Dependencies: pycryptodome (for AES operations)