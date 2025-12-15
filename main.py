#!/usr/bin/env python3

import sys
import os
from src.cli import parse_arguments, validate_arguments, hex_to_bytes_or_empty
from src.file_io import read_file, write_file, safe_write_file, cleanup_failed_output
from src.modes import get_mode
from src.aead import EncryptThenMAC

def main():
   
    args = parse_arguments()
    args = validate_arguments(args)
    
    
    key = bytes.fromhex(args.key)
    iv = hex_to_bytes_or_empty(args.iv) if args.iv else None
    aad = hex_to_bytes_or_empty(args.aad) if args.aad else b""
    
    
    input_data = read_file(args.input)
    
    try:
        if args.mode == 'gcm':
            # Handle GCM mode
            from src.modes.gcm import GCM, AuthenticationError
            
            if args.encrypt:
                # GCM Encryption
                cipher = GCM(key, nonce=iv)
                output = cipher.encrypt(input_data, aad)
                
                if args.verbose:
                    nonce = output[:12]
                    tag = output[-16:]
                    ciphertext = output[12:-16]
                    print(f"[GCM] Nonce: {nonce.hex()}")
                    print(f"[GCM] Ciphertext length: {len(ciphertext)} bytes")
                    print(f"[GCM] Tag: {tag.hex()[:16]}...")
                    print(f"[SUCCESS] Encryption completed successfully")
                
                safe_write_file(args.output, output)
                
            else:  
                try:
                    cipher = GCM(key, nonce=iv)
                    output = cipher.decrypt(input_data, aad)
                    
                    if args.verbose:
                        print(f"[GCM] Decryption successful")
                        print(f"[GCM] Plaintext length: {len(output)} bytes")
                    
                    safe_write_file(args.output, output)
                    print("[SUCCESS] Decryption completed successfully")
                    
                except AuthenticationError as e:
                    print(f"[ERROR] {e}", file=sys.stderr)
                    print("[ERROR] Authentication failed: AAD mismatch or ciphertext tampered", 
                          file=sys.stderr)
                    cleanup_failed_output(args.output)
                    sys.exit(1)
                    
        elif args.mode in ['ecb', 'cbc', 'ctr']:
            
            cipher = get_mode(args.mode, key, iv=iv)
            
            if args.encrypt:
                output = cipher.encrypt(input_data)
                if args.verbose:
                    print(f"[{args.mode.upper()}] Encryption completed")
            else:
                output = cipher.decrypt(input_data)
                if args.verbose:
                    print(f"[{args.mode.upper()}] Decryption completed")
            
            safe_write_file(args.output, output)
            
        else:
            print(f"Unsupported mode: {args.mode}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Operation failed: {e}", file=sys.stderr)
        cleanup_failed_output(args.output)
        sys.exit(1)

if __name__ == "__main__":
    main()
