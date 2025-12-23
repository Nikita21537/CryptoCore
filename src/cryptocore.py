import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))


from src.cli_parser import parse_args
from src.file_io import (read_file_with_iv, write_file_with_iv,
                        read_gcm_file, read_etm_file)
from src.modes import create_mode
from src.csprng import generate_aes_key, print_key_info, generate_random_bytes
from src.hash import create_hash
from src.mac.__init__ import HMACStream, parse_hmac_file
from src.modes.gcm import GCM, AuthenticationError as GCMAuthError
from src.modes.encrypt_then_mac import EncryptThenMAC, AuthenticationError as ETMAuthError
from src.kdf import pbkdf2_hmac_sha256, derive_key


def needs_iv_in_file(mode: str) -> bool:

    return mode.lower() in ['cbc', 'cfb', 'ofb', 'ctr']


def run_encryption(args):

    try:
        # Handle key
        if args.key_bytes:
            key_bytes = args.key_bytes
            print_key_info(key_bytes, source="provided")
        else:
            # Generate key for encryption
            if not args.encrypt:
                print("Error: Key required for decryption", file=sys.stderr)
                sys.exit(1)

            key_bytes = generate_aes_key()
            print_key_info(key_bytes, source="generated")
            print("[INFO] Please save this key for decryption!", file=sys.stderr)

        # Handle IV/Nonce
        iv_bytes = args.iv_bytes

        # Read input data based on mode
        if args.mode.lower() == 'gcm':
            if args.decrypt:
                # For GCM decryption, read special format
                nonce, input_data, tag = read_gcm_file(args.input)
                input_data = nonce + input_data + tag
                iv_bytes = nonce
            else:
                # For GCM encryption, read plain file
                _, input_data = read_file_with_iv(args.input, has_iv=False)

        elif args.mode.lower() == 'etm':
            if args.decrypt:
                # For ETM decryption, read with IV and tag
                iv_bytes, ciphertext, tag = read_etm_file(args.input, has_iv=True)
                input_data = (iv_bytes or b"") + ciphertext + tag
            else:
                _, input_data = read_file_with_iv(args.input, has_iv=False)

        elif args.decrypt and not iv_bytes and needs_iv_in_file(args.mode):
            # For other modes with IV, read from file
            iv_bytes, input_data = read_file_with_iv(args.input, has_iv=True)
        else:
            _, input_data = read_file_with_iv(args.input, has_iv=False)

        # Execute based on mode
        if args.mode.lower() == 'gcm':
            _run_gcm(args, key_bytes, iv_bytes, input_data)

        elif args.mode.lower() == 'etm':
            _run_etm(args, key_bytes, iv_bytes, input_data)

        else:
            _run_standard_mode(args, key_bytes, iv_bytes, input_data)

    except (ValueError, GCMAuthError, ETMAuthError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        _cleanup_failed_file(args.output)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        _cleanup_failed_file(args.output)
        sys.exit(1)


def _run_gcm(args, key_bytes, nonce_bytes, input_data):

    gcm = GCM(key_bytes, nonce_bytes)

    if args.encrypt:
        ciphertext = gcm.encrypt(input_data, args.aad_bytes)
        write_file_with_iv(args.output, None, ciphertext)

        print(f"[INFO] Generated nonce (hex): {gcm.nonce.hex()}")
        print(f"[INFO] Nonce written to beginning of output file")
        print(f"Successfully encrypted {args.input} -> {args.output}")

    else:
        try:
            plaintext = gcm.decrypt(input_data, args.aad_bytes)
            write_file_with_iv(args.output, None, plaintext)
            print(f"[SUCCESS] GCM decryption completed successfully")
            print(f"Successfully decrypted {args.input} -> {args.output}")

        except GCMAuthError:
            print(f"[ERROR] GCM authentication failed: AAD mismatch or ciphertext tampered",
                  file=sys.stderr)
            _cleanup_failed_file(args.output)
            sys.exit(1)


def _run_etm(args, key_bytes, iv_bytes, input_data):

    # Determine base mode (default to CBC)
    base_mode = 'cbc'
    if args.mode.lower() == 'etm':
        # Could parse from args if extended
        pass

    etm = EncryptThenMAC(base_mode, key_bytes, iv_bytes)

    if args.encrypt:
        ciphertext = etm.encrypt(input_data, args.aad_bytes)
        write_file_with_iv(args.output, None, ciphertext)

        if iv := etm.get_iv():
            print(f"[INFO] Generated IV (hex): {iv.hex()}")

        print(f"Successfully encrypted {args.input} -> {args.output}")

    else:
        try:
            plaintext = etm.decrypt(input_data, args.aad_bytes)
            write_file_with_iv(args.output, None, plaintext)
            print(f"[SUCCESS] Encrypt-then-MAC decryption completed successfully")
            print(f"Successfully decrypted {args.input} -> {args.output}")

        except ETMAuthError:
            print(f"[ERROR] Encrypt-then-MAC authentication failed",
                  file=sys.stderr)
            _cleanup_failed_file(args.output)
            sys.exit(1)


def _run_standard_mode(args, key_bytes, iv_bytes, input_data):

    cipher = create_mode(args.mode, key_bytes, iv_bytes)

    if args.encrypt:
        output_data = cipher.encrypt(input_data)

        if needs_iv_in_file(args.mode):
            write_file_with_iv(args.output, cipher.iv, output_data)
            print(f"[INFO] Generated IV (hex): {cipher.get_iv_hex()}")
            print(f"[INFO] IV written to beginning of output file")
        else:
            write_file_with_iv(args.output, None, output_data)

        operation = "encrypted"

    else:
        output_data = cipher.decrypt(input_data)
        write_file_with_iv(args.output, None, output_data)
        operation = "decrypted"

    print(f"Successfully {operation} {args.input} -> {args.output}")


def _cleanup_failed_file(filepath: str):

    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"[INFO] Removed partially created file: {filepath}")
        except OSError:
            pass


def run_hash(args):

    try:
        # Handle stdin
        if args.input == '-':
            input_data = sys.stdin.buffer.read()
            input_name = 'stdin'

            if args.hmac or args.cmac:
                result = _compute_mac_direct(args, input_data)
            else:
                result = _compute_hash_direct(args, input_data)

        else:
            input_name = args.input

            if args.hmac or args.cmac:
                result = _compute_mac_streaming(args, input_name)
            else:
                result = _compute_hash_streaming(args, input_name)

        # Verification mode
        if args.verify:
            _verify_mac(args, input_name, result)
            return

        # Output result
        output_line = f"{result}  {input_name}"

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_line + '\n')
            print(f"Output written to {args.output}")
        else:
            print(output_line)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _compute_hash_direct(args, data: bytes) -> str:

    hash_obj = create_hash(args.algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()


def _compute_hash_streaming(args, filepath: str) -> str:

    hash_obj = create_hash(args.algorithm)

    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def _compute_mac_direct(args, data: bytes) -> str:

    if args.hmac:
        from .mac import HMAC
        hmac = HMAC(args.key_bytes, args.algorithm)
        return hmac.compute_hex(data)
    else:
        from .mac import AESCMAC
        cmac = AESCMAC(args.key_bytes)
        return cmac.compute_hex(data)


def _compute_mac_streaming(args, filepath: str) -> str:

    if args.hmac:
        hmac_stream = HMACStream(args.key_bytes, args.algorithm)

        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hmac_stream.update(chunk)

        return hmac_stream.finalize_hex()
    else:
        # CMAC needs entire data
        with open(filepath, 'rb') as f:
            data = f.read()

        from .mac import AESCMAC
        cmac = AESCMAC(args.key_bytes)
        return cmac.compute_hex(data)


def _verify_mac(args, input_name: str, computed_value: str):

    try:
        expected_value, _ = parse_hmac_file(args.verify)

        if computed_value == expected_value:
            print(f"[OK] MAC verification successful for {input_name}")
            sys.exit(0)
        else:
            print(f"[ERROR] MAC verification failed for {input_name}", file=sys.stderr)
            print(f"  Computed: {computed_value}", file=sys.stderr)
            print(f"  Expected: {expected_value}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}", file=sys.stderr)
        sys.exit(1)


def run_derive(args):

    try:
        # Security warning for low iterations
        if args.iterations < 100000:
            print(f"[WARNING] Using low iteration count ({args.iterations}). "
                  f"For production, use at least 100,000 iterations.",
                  file=sys.stderr)

        # Generate salt if not provided
        if args.salt_bytes is None:
            salt_bytes = generate_random_bytes(16)
            print(f"[INFO] Generated random salt (hex): {salt_bytes.hex()}")
        else:
            salt_bytes = args.salt_bytes
            print(f"[INFO] Using provided salt (hex): {salt_bytes.hex()}")

        print(f"[INFO] Deriving {args.length}-byte key with {args.iterations} iterations...")

        # Perform key derivation
        if args.algorithm.lower() == 'pbkdf2':
            derived_key = pbkdf2_hmac_sha256(
                password=args.password,
                salt=salt_bytes,
                iterations=args.iterations,
                dklen=args.length
            )
        else:
            print(f"Error: Unsupported KDF algorithm: {args.algorithm}", file=sys.stderr)
            sys.exit(1)

        # Clear password from memory ASAP
        args.password = None

        # Print key statistics
        ones_count = sum(bin(b).count('1') for b in derived_key)
        total_bits = len(derived_key) * 8
        ones_percentage = (ones_count / total_bits) * 100

        print(f"[INFO] Derived key statistics: {ones_count}/{total_bits} "
              f"bits set to 1 ({ones_percentage:.1f}%)")

        # Output results
        if args.raw:
            # Output raw binary key
            if args.output:
                with open(args.output, 'wb') as f:
                    f.write(derived_key)
                print(f"[INFO] Raw key written to {args.output}")
            else:
                sys.stdout.buffer.write(derived_key)
        else:
            # Output hex format: KEY_HEX SALT_HEX
            output_line = f"{derived_key.hex()} {salt_bytes.hex()}"

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output_line + '\n')
                print(f"[INFO] Derived key written to {args.output}")

                # Also write raw key to .bin file
                raw_output = f"{args.output}.bin"
                with open(raw_output, 'wb') as f:
                    f.write(derived_key)
                print(f"[INFO] Raw binary key written to {raw_output}")
            else:
                print(output_line)

        # Additional info for key hierarchy example
        if args.length >= 32:
            print("\n[INFO] Example key hierarchy usage:")
            print("  Master key (first 32 bytes): " + derived_key[:32].hex())
            print("  Encryption key: " + derive_key(derived_key[:32], "encryption", 32).hex()[:16] + "...")
            print("  Authentication key: " + derive_key(derived_key[:32], "authentication", 32).hex()[:16] + "...")

    except ValueError as e:
        print(f"[ERROR] Invalid parameters: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Key derivation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():

    args = parse_args()

    if args.command == 'enc':
        run_encryption(args)
    elif args.command == 'dgst':
        run_hash(args)
    elif args.command == 'derive':  # NEW COMMAND
        run_derive(args)
    else:
        print(f"Error: Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()