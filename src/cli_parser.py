import argparse
import sys
import os
from typing import Tuple, Optional, List


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description='CryptoCore - Cryptographic Tool with Key Derivation Support',
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Encryption/decryption parser
    enc_parser = subparsers.add_parser('enc', help='Encryption/decryption', add_help=False)
    enc_parser.set_defaults(command='enc')

    # Required arguments for encryption
    enc_parser.add_argument('--algorithm', required=True,
                            help='Cipher algorithm (only "aes" supported)')
    enc_parser.add_argument('--mode', required=True,
                            help='Mode: ecb, cbc, cfb, ofb, ctr, gcm, etm')

    # Operation
    enc_group = enc_parser.add_mutually_exclusive_group(required=True)
    enc_group.add_argument('--encrypt', action='store_true',
                           help='Encrypt the input file')
    enc_group.add_argument('--decrypt', action='store_true',
                           help='Decrypt the input file')

    # Key
    enc_parser.add_argument('--key',
                            help='Key as hexadecimal string')

    # File I/O
    enc_parser.add_argument('--input', required=True,
                            help='Input file path')
    enc_parser.add_argument('--output',
                            help='Output file path (optional)')

    # IV/Nonce
    enc_parser.add_argument('--iv',
                            help='IV/Nonce as hexadecimal string')

    # AAD for authenticated modes
    enc_parser.add_argument('--aad',
                            help='Associated Authenticated Data as hex string (for GCM/ETM)')

    # Hash/MAC parser
    hash_parser = subparsers.add_parser('dgst', help='Compute hash or MAC', add_help=False)
    hash_parser.set_defaults(command='dgst')

    hash_parser.add_argument('--algorithm', required=True,
                             help='Hash algorithm: sha256, sha3-256')
    hash_parser.add_argument('--input', required=True,
                             help='Input file path (use - for stdin)')
    hash_parser.add_argument('--output',
                             help='Output file for hash (optional)')

    # MAC options
    hash_parser.add_argument('--hmac', action='store_true',
                             help='Enable HMAC mode')
    hash_parser.add_argument('--cmac', action='store_true',
                             help='Enable AES-CMAC mode')
    hash_parser.add_argument('--key',
                             help='Key for MAC (hex string)')
    hash_parser.add_argument('--verify',
                             help='Verify against existing MAC file')

    # Key derivation parser (NEW FOR SPRINT 7)
    derive_parser = subparsers.add_parser('derive', help='Key derivation from password', add_help=False)
    derive_parser.set_defaults(command='derive')

    derive_parser.add_argument('--password', required=True,
                               help='Password string (use quotes for special characters)')
    derive_parser.add_argument('--salt',
                               help='Salt as hexadecimal string (auto-generated if omitted)')
    derive_parser.add_argument('--iterations', type=int, default=100000,
                               help='Iteration count (default: 100000)')
    derive_parser.add_argument('--length', type=int, default=32,
                               help='Key length in bytes (default: 32)')
    derive_parser.add_argument('--algorithm', default='pbkdf2',
                               help='KDF algorithm (only pbkdf2 supported)')
    derive_parser.add_argument('--output',
                               help='Output file for key (optional)')
    derive_parser.add_argument('--raw',
                               action='store_true',
                               help='Output raw binary key instead of hex')

    # Parse arguments
    args = parser.parse_args()

    # Handle legacy style (no subcommand)
    if args.command is None:
        return _parse_legacy_args()

    # Validate based on command
    if args.command == 'enc':
        return _validate_encryption_args(args)
    elif args.command == 'dgst':
        return _validate_hash_args(args)
    elif args.command == 'derive':
        return _validate_derive_args(args)

    return args


def _parse_legacy_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--algorithm', required=True)
    parser.add_argument('--mode', required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encrypt', action='store_true')
    group.add_argument('--decrypt', action='store_true')

    parser.add_argument('--key')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output')
    parser.add_argument('--iv')
    parser.add_argument('--aad')

    args = parser.parse_args()
    args.command = 'enc'
    return _validate_encryption_args(args)


def _validate_encryption_args(args: argparse.Namespace) -> argparse.Namespace:

    errors = []

    # Algorithm validation
    if args.algorithm.lower() != 'aes':
        errors.append(f"Only 'aes' algorithm supported, got '{args.algorithm}'")

    # Mode validation
    valid_modes = ['ecb', 'cbc', 'cfb', 'ofb', 'ctr', 'gcm', 'etm']
    if args.mode.lower() not in valid_modes:
        errors.append(f"Invalid mode '{args.mode}'. Valid: {', '.join(valid_modes)}")

    # Key validation
    key_bytes = None
    if args.key:
        try:
            key_bytes = bytes.fromhex(args.key)
            # GCM and standard modes need at least 16 bytes
            if args.mode.lower() in ['gcm', 'etm'] and len(key_bytes) < 16:
                errors.append(f"{args.mode.upper()} requires at least 16-byte key")
        except ValueError:
            errors.append(f"Invalid hexadecimal key: {args.key}")
    elif args.decrypt:
        errors.append("Key required for decryption")

    # IV/Nonce validation
    iv_bytes = None
    if args.iv:
        try:
            iv_bytes = bytes.fromhex(args.iv)
            # GCM uses 12-byte nonce by default
            if args.mode.lower() == 'gcm' and len(iv_bytes) != 12:
                print(f"[INFO] GCM typically uses 12-byte nonce, got {len(iv_bytes)}",
                      file=sys.stderr)
        except ValueError:
            errors.append(f"Invalid hexadecimal IV/nonce: {args.iv}")
    elif args.encrypt and args.mode.lower() in ['cbc', 'cfb', 'ofb', 'ctr']:
        # IV will be auto-generated
        pass

    # AAD validation
    aad_bytes = b""
    if args.aad:
        try:
            aad_bytes = bytes.fromhex(args.aad)
        except ValueError:
            errors.append(f"Invalid hexadecimal AAD: {args.aad}")

    # File validation
    if args.input != '-' and not os.path.exists(args.input):
        errors.append(f"Input file does not exist: {args.input}")

    # Auto-generate output filename
    if not args.output:
        if args.encrypt:
            if args.input == '-':
                args.output = 'encrypted.bin'
            else:
                args.output = f"{args.input}.enc"
        else:
            if args.input == '-':
                args.output = 'decrypted.bin'
            elif args.input.endswith('.enc'):
                args.output = args.input[:-4] + '.dec'
            else:
                args.output = f"{args.input}.dec"

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Store parsed values
    args.key_bytes = key_bytes
    args.iv_bytes = iv_bytes
    args.aad_bytes = aad_bytes

    return args


def _validate_hash_args(args: argparse.Namespace) -> argparse.Namespace:

    errors = []

    # Algorithm validation
    valid_algorithms = ['sha256', 'sha3-256']
    if args.algorithm.lower() not in valid_algorithms:
        errors.append(f"Invalid algorithm. Valid: {', '.join(valid_algorithms)}")

    # MAC mode validation
    if args.hmac and args.cmac:
        errors.append("Cannot use both --hmac and --cmac")

    # Key validation for MAC modes
    key_bytes = None
    if args.hmac or args.cmac:
        if not args.key:
            errors.append("Key required for MAC modes")
        else:
            try:
                key_bytes = bytes.fromhex(args.key)
                if args.cmac and len(key_bytes) != 16:
                    errors.append("AES-CMAC requires 16-byte key")
            except ValueError:
                errors.append(f"Invalid hexadecimal key: {args.key}")

    # File validation
    if args.verify and not os.path.exists(args.verify):
        errors.append(f"Verify file does not exist: {args.verify}")

    if args.input != '-' and not os.path.exists(args.input):
        errors.append(f"Input file does not exist: {args.input}")

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    args.key_bytes = key_bytes
    return args


def _validate_derive_args(args: argparse.Namespace) -> argparse.Namespace:

    errors = []

    # Algorithm validation
    valid_algorithms = ['pbkdf2']
    if args.algorithm.lower() not in valid_algorithms:
        errors.append(f"Invalid KDF algorithm. Valid: {', '.join(valid_algorithms)}")

    # Iterations validation
    if args.iterations <= 0:
        errors.append("Iterations must be positive")
    elif args.iterations < 10000:
        print(f"[WARNING] Low iteration count ({args.iterations}). "
              f"Consider using at least 100,000 for security.",
              file=sys.stderr)

    # Length validation
    if args.length <= 0:
        errors.append("Key length must be positive")
    elif args.length > 1024:  # Reasonable upper limit
        errors.append(f"Key length too large ({args.length} > 1024 bytes)")

    # Salt validation
    salt_bytes = None
    if args.salt:
        try:
            salt_bytes = bytes.fromhex(args.salt)
            if len(salt_bytes) < 8:
                print(f"[WARNING] Salt is short ({len(salt_bytes)} bytes). "
                      f"Recommend at least 16 bytes for security.",
                      file=sys.stderr)
        except ValueError:
            # If not hex, treat as UTF-8 string
            salt_bytes = args.salt.encode('utf-8')
            print(f"[INFO] Using salt as UTF-8 string: {args.salt}",
                  file=sys.stderr)

    # Output file validation
    if args.output:
        output_dir = os.path.dirname(args.output) or '.'
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                errors.append(f"Cannot create output directory: {e}")

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Store parsed values
    args.salt_bytes = salt_bytes

    return args