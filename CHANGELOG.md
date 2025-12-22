# Changelog

All notable changes to CryptoCore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [8.0.0] - 2024-01-20

### Added
- Comprehensive documentation system:
  - `docs/API.md` - Complete API reference
  - `docs/USERGUIDE.md` - User guide with examples
  - `docs/DEVELOPMENT.md` - Developer guide
- Professional test suite:
  - Unit tests for all modules
  - Integration tests for CLI
  - Known-answer tests (NIST/RFC vectors)
  - Performance benchmarks
  - Interoperability tests
  - Memory safety tests
- Quality assurance infrastructure:
  - `.pylintrc` configuration
  - `pyproject.toml` build system
  - Code coverage reporting
  - Type checking with mypy
- Security review checklist
- Example code in `examples/` directory

### Changed
- Refactored code for better organization
- Improved error handling and messages
- Enhanced security of sensitive data handling
- Updated all documentation with examples
- Standardized code style (PEP 8 compliance)

### Fixed
- Memory leak in large file processing
- Timing side-channels in HMAC verification
- Edge cases in PKCS#7 padding
- File I/O error handling

### Security
- Implemented constant-time comparisons
- Secure memory clearing for sensitive data
- Input validation for all parameters
- Protection against common cryptographic pitfalls

## [7.0.0] - 2024-01-15

### Added
- Key Derivation Functions (Sprint 7):
  - PBKDF2-HMAC-SHA256 from scratch (RFC 2898)
  - Key hierarchy function for deriving subkeys
  - New `derive` CLI command
  - Support for RFC 6070 test vectors
- Salt generation and management
- Performance benchmarks for key derivation

### Changed
- Updated CLI parser for new `derive` command
- Enhanced csprng module with salt generation
- Updated README with key derivation documentation

## [6.0.0] - 2024-01-10

### Added
- Authenticated encryption modes:
  - GCM (Galois/Counter Mode)
  - Encrypt-then-MAC
- Associated Authenticated Data (AAD) support
- Authentication failure handling (no output on failure)

### Changed
- Refactored mode architecture for extensibility
- Improved file format for authenticated modes
- Enhanced error messages for authentication failures

## [5.0.0] - 2024-01-05

### Added
- Message Authentication Codes:
  - HMAC-SHA256 from scratch (RFC 2104)
  - AES-CMAC (bonus feature)
  - Streaming HMAC for large files
- HMAC verification functionality
- CLI support for HMAC generation/verification

### Changed
- Updated hash module architecture
- Enhanced CLI with HMAC options
- Improved test coverage

## [4.0.0] - 2023-12-28

### Added
- Hash functions from scratch:
  - SHA-256 (NIST FIPS 180-4)
  - SHA3-256 (Keccak sponge)
- Hash streaming for large files
- CLI `dgst` command for hashing
- Interoperability with system tools

### Changed
- Restructured project for hash module
- Updated documentation with hash examples

## [3.0.0] - 2023-12-20

### Added
- Cryptographically Secure RNG:
  - Secure random byte generation
  - Weak key detection
  - Key statistics reporting
- Automatic key generation for encryption
- File format improvements

### Changed
- Enhanced security warnings
- Improved user feedback
- Updated installation instructions

## [2.0.0] - 2023-12-15

### Added
- Multiple encryption modes:
  - CBC (Cipher Block Chaining)
  - CFB (Cipher Feedback)
  - OFB (Output Feedback)
  - CTR (Counter)
- IV handling and auto-generation
- Interoperability with OpenSSL

### Changed
- Refactored mode architecture
- Improved file I/O for IV handling
- Enhanced test suite

## [1.0.0] - 2023-12-10

### Added
- Initial release
- AES-128 ECB mode with PKCS#7 padding
- Basic CLI interface
- File encryption/decryption
- Basic test framework

## Upgrade Notes

### From 7.x to 8.0
- No breaking API changes
- Enhanced documentation structure
- Improved test coverage
- Better security practices

### From 6.x to 7.0
- New `derive` command added
- PBKDF2 implementation
- Key hierarchy functions

### From 5.x to 6.0
- GCM and Encrypt-then-MAC modes
- AAD support for authenticated encryption

## Deprecations

- None currently

## Security Advisories

- Always use authenticated encryption (GCM or Encrypt-then-MAC) for sensitive data
- Never reuse nonces with the same key in GCM mode
- Use at least 100,000 iterations for PBKDF2
- Always use cryptographically secure random keys