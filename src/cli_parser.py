import argparse
import sys
import os
from typing import Optional

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='CryptoCore - Cryptographic Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    
    parser.add_argument('--algorithm', '-a', 
                       choices=['aes'], 
                       default='aes',
                       help='Encryption algorithm (default: aes)')
    
    parser.add_argument('--mode', '-m',
                       choices=['ecb', 'cbc', 'ctr', 'gcm'],
                       default='ecb',
                       help='Block cipher mode (default: ecb)')
    
    parser.add_argument('--key', '-k',
                       required=True,
                       help='Encryption key as hex string')
    
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encrypt', '-e',
                      action='store_true',
                      help='Encrypt mode')
    group.add_argument('--decrypt', '-d',
                      action='store_true',
                      help='Decrypt mode')
    
   
    parser.add_argument('--input', '-i',
                       required=True,
                       help='Input file path')
    
    parser.add_argument('--output', '-o',
                       required=True,
                       help='Output file path')
    
   
    parser.add_argument('--iv',
                       help='Initialization Vector or Nonce as hex string '
                            '(for CBC, CTR, GCM modes)')
    
   
    parser.add_argument('--aad',
                       help='Associated Authenticated Data as hex string '
                            '(for GCM mode)')
    
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')
    
    return parser.parse_args()

def validate_arguments(args):
   
    errors = []
    
    
    try:
        key_bytes = bytes.fromhex(args.key)
        if len(key_bytes) not in (16, 24, 32):
            errors.append("Key must be 16, 24, or 32 bytes (32, 48, or 64 hex chars)")
    except ValueError:
        errors.append("Key must be a valid hex string")
    
    
    if args.mode in ['cbc', 'ctr'] and not args.iv:
        errors.append(f"{args.mode.upper()} mode requires --iv")
    

    if args.mode == 'gcm' and args.iv:
        try:
            iv_bytes = bytes.fromhex(args.iv)
            if len(iv_bytes) != 12:
                errors.append("GCM nonce must be 12 bytes (24 hex chars)")
        except ValueError:
            errors.append("IV/Nonce must be a valid hex string")
    
    if args.aad:
        try:
            aad_bytes = bytes.fromhex(args.aad)
        except ValueError:
            errors.append("AAD must be a valid hex string")
    
    if errors:
        print("Argument errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    return args

def hex_to_bytes_or_empty(hex_str: Optional[str]) -> bytes:
    
    if not hex_str:
        return b""
    return bytes.fromhex(hex_str)
