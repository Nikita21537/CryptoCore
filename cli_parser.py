import argparse
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(description='CryptoCore - Cryptographic Tool')
    
    parser.add_argument('--algorithm', required=True, choices=['aes'],
                        help='Cryptographic algorithm (only AES supported)')
    parser.add_argument('--mode', required=True, 
                        choices=['ecb', 'cbc', 'cfb', 'ofb', 'ctr'],
                        help='Mode of operation')
    parser.add_argument('--key', required=True,
                        help='Encryption key as hexadecimal string')
    
    # Операции (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('--encrypt', action='store_true',
                                help='Perform encryption')
    operation_group.add_argument('--decrypt', action='store_true',
                                help='Perform decryption')
    
    parser.add_argument('--input', required=True,
                        help='Input file path')
    parser.add_argument('--output',
                        help='Output file path (default: derived from input)')
    parser.add_argument('--iv',
                        help='Initialization Vector for decryption (hex string)')
    
    args = parser.parse_args()
    
    # Валидация ключа
    try:
        key_bytes = bytes.fromhex(args.key)
        if len(key_bytes) != 16:
            raise ValueError("AES-128 key must be 16 bytes (32 hex characters)")
    except ValueError as e:
        print(f"Error: Invalid key format - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Валидация IV
    if args.iv:
        if args.encrypt:
            print("Warning: IV provided during encryption - it will be ignored", file=sys.stderr)
        else:
            try:
                iv_bytes = bytes.fromhex(args.iv)
                if len(iv_bytes) != 16:
                    raise ValueError("IV must be 16 bytes (32 hex characters)")
            except ValueError as e:
                print(f"Error: Invalid IV format - {e}", file=sys.stderr)
                sys.exit(1)
    
    # Генерация имени выходного файла по умолчанию
    if not args.output:
        args.output = generate_output_filename(args.input, args.encrypt, args.mode)
    
    return args

def generate_output_filename(input_file, is_encrypt, mode):
    if is_encrypt:
        return f"{input_file}.{mode}.enc"
    else:
        if input_file.endswith(f'.{mode}.enc'):
            return input_file.replace(f'.{mode}.enc', f'.{mode}.dec')
        else:
            return f"{input_file}.dec"
