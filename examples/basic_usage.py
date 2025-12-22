import os
import sys
import tempfile
import subprocess

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cryptocore.kdf import pbkdf2_hmac_sha256, derive_key


def example_encryption():

    print("=" * 60)
    print("Example 1: File Encryption & Decryption")
    print("=" * 60)

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        original_content = b"""This is a secret document.
It contains sensitive information that needs protection.
Never store passwords in plain text!
Use strong encryption like AES-256 with GCM mode."""
        f.write(original_content)
        input_file = f.name

    encrypted_file = input_file + '.enc'
    decrypted_file = input_file + '.dec'

    key = os.urandom(16)  # 128-bit key

    try:
        print(f"Input file: {input_file}")
        print(f"Key: {key.hex()}")

        # Encrypt using CBC mode
        print("\nEncrypting with AES-128 CBC...")
        subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
            '--encrypt', '--key', key.hex(),
            '--input', input_file, '--output', encrypted_file
        ], check=True)

        print(f"Encrypted file: {encrypted_file}")
        print(f"File size: {os.path.getsize(encrypted_file)} bytes")

        # Decrypt
        print("\nDecrypting...")
        subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
            '--decrypt', '--key', key.hex(),
            '--input', encrypted_file, '--output', decrypted_file
        ], check=True)

        print(f"Decrypted file: {decrypted_file}")

        # Verify content matches
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()

        if original_content == decrypted_content:
            print("✅ Success! Original and decrypted content match.")
        else:
            print("❌ Error! Content mismatch.")

    finally:
        # Clean up
        for f in [input_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.unlink(f)


def example_authenticated_encryption():

    print("\n" + "=" * 60)
    print("Example 2: Authenticated Encryption (GCM)")
    print("=" * 60)

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        sensitive_data = b"""Financial Transaction Record
Date: 2024-01-20
Amount: $1,000,000.00
Recipient: Secure Bank Account
Reference: TXN-2024-001"""
        f.write(sensitive_data)
        input_file = f.name

    encrypted_file = input_file + '.gcm'
    decrypted_file = input_file + '.dec'

    key = os.urandom(16)
    aad = b"financial_record_v1"  # Authenticated but not encrypted

    try:
        print(f"Input file: {input_file}")
        print(f"Key: {key.hex()}")
        print(f"AAD: {aad.hex()}")

        # Encrypt with GCM
        print("\nEncrypting with AES-128 GCM...")
        result = subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'gcm',
            '--encrypt', '--key', key.hex(), '--aad', aad.hex(),
            '--input', input_file, '--output', encrypted_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Encryption failed: {result.stderr}")
            return

        print(f"Encrypted file: {encrypted_file}")

        # Extract nonce from output
        import re
        match = re.search(r'Generated nonce \(hex\): ([0-9a-f]{24})', result.stdout)
        if match:
            print(f"Nonce: {match.group(1)}")

        # Decrypt with correct AAD
        print("\nDecrypting with correct AAD...")
        result = subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'gcm',
            '--decrypt', '--key', key.hex(), '--aad', aad.hex(),
            '--input', encrypted_file, '--output', decrypted_file
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Decryption successful with correct AAD")

            with open(decrypted_file, 'rb') as f:
                decrypted = f.read()

            if sensitive_data == decrypted:
                print("✅ Content verified")
            else:
                print("❌ Content mismatch")
        else:
            print("❌ Decryption failed")

        # Try with wrong AAD (should fail)
        print("\nTrying decryption with wrong AAD...")
        wrong_aad = b"tampered_record"
        result = subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'gcm',
            '--decrypt', '--key', key.hex(), '--aad', wrong_aad.hex(),
            '--input', encrypted_file, '--output', decrypted_file + '.wrong'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("✅ Correctly rejected wrong AAD (authentication failed)")
            print(f"  Error: {result.stderr.strip()}")
        else:
            print("❌ Should have failed with wrong AAD")

    finally:
        for f in [input_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.unlink(f)
        if os.path.exists(decrypted_file + '.wrong'):
            os.unlink(decrypted_file + '.wrong')


def example_hashing():

    print("\n" + "=" * 60)
    print("Example 3: File Integrity Checking")
    print("=" * 60)

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.iso') as f:
        # Simulate a downloaded file
        file_content = b"Fake ISO file content " * 1000
        f.write(file_content)
        downloaded_file = f.name

    hash_file = downloaded_file + '.sha256'

    try:
        print(f"File: {downloaded_file}")
        print(f"Size: {len(file_content):,} bytes")

        # Compute SHA-256 hash
        print("\nComputing SHA-256 hash...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256',
            '--input', downloaded_file, '--output', hash_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Hash computation failed: {result.stderr}")
            return

        # Read the hash
        with open(hash_file, 'r') as f:
            hash_line = f.read().strip()

        file_hash = hash_line.split()[0]
        print(f"SHA-256 hash: {file_hash}")
        print(f"Hash saved to: {hash_file}")

        # Verify the hash
        print("\nVerifying hash...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256',
            '--input', downloaded_file
        ], capture_output=True, text=True)

        computed_hash = result.stdout.strip().split()[0]

        if computed_hash == file_hash:
            print("✅ Hash verification passed")
        else:
            print("❌ Hash verification failed")
            print(f"  Computed: {computed_hash}")
            print(f"  Expected: {file_hash}")

        # Simulate file tampering
        print("\nSimulating file tampering...")
        with open(downloaded_file, 'ab') as f:
            f.write(b"tampered")  # Append bytes

        print("Recomputing hash after tampering...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256',
            '--input', downloaded_file
        ], capture_output=True, text=True)

        new_hash = result.stdout.strip().split()[0]

        if new_hash != file_hash:
            print("✅ Tampering detected! Hashes differ.")
            print(f"  Original: {file_hash[:16]}...")
            print(f"  After tamper: {new_hash[:16]}...")
        else:
            print("❌ Tampering not detected (unexpected)")

    finally:
        for f in [downloaded_file, hash_file]:
            if os.path.exists(f):
                os.unlink(f)


def example_hmac():

    print("\n" + "=" * 60)
    print("Example 4: Message Authentication Codes (HMAC)")
    print("=" * 60)

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
        firmware = b"Firmware v2.1.0 binary data " * 100
        f.write(firmware)
        firmware_file = f.name

    hmac_file = firmware_file + '.hmac'
    key = os.urandom(32)  # 256-bit HMAC key

    try:
        print(f"Firmware file: {firmware_file}")
        print(f"HMAC key: {key.hex()[:16]}...")

        # Generate HMAC
        print("\nGenerating HMAC-SHA256...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256', '--hmac',
            '--key', key.hex(), '--input', firmware_file, '--output', hmac_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"HMAC generation failed: {result.stderr}")
            return

        # Read HMAC
        with open(hmac_file, 'r') as f:
            hmac_line = f.read().strip()

        hmac_value = hmac_line.split()[0]
        print(f"HMAC: {hmac_value[:16]}...")
        print(f"HMAC saved to: {hmac_file}")

        # Verify with correct key
        print("\nVerifying with correct key...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256', '--hmac',
            '--key', key.hex(), '--input', firmware_file, '--verify', hmac_file
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ HMAC verification passed with correct key")
        else:
            print("❌ HMAC verification failed")

        # Verify with wrong key (should fail)
        print("\nVerifying with wrong key...")
        wrong_key = os.urandom(32)
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256', '--hmac',
            '--key', wrong_key.hex(), '--input', firmware_file, '--verify', hmac_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("✅ Correctly rejected wrong key")
        else:
            print("❌ Should have failed with wrong key")

        # Simulate firmware tampering
        print("\nSimulating firmware tampering...")
        with open(firmware_file, 'ab') as f:
            f.write(b"malicious_code")

        print("Verifying after tampering...")
        result = subprocess.run([
            'cryptocore', 'dgst', '--algorithm', 'sha256', '--hmac',
            '--key', key.hex(), '--input', firmware_file, '--verify', hmac_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("✅ Tampering detected!")
        else:
            print("❌ Tampering not detected (unexpected)")

    finally:
        for f in [firmware_file, hmac_file]:
            if os.path.exists(f):
                os.unlink(f)


def example_key_derivation():
    """Example: Key derivation from passwords."""
    print("\n" + "=" * 60)
    print("Example 5: Key Derivation from Passwords")
    print("=" * 60)

    # User password
    password = "MySecureDatabasePassword!2024"

    print(f"Password: {password}")
    print("(In real applications, never print passwords!)")

    # Derive key using PBKDF2
    print("\nDeriving encryption key with PBKDF2...")
    print("Parameters: 100,000 iterations, 32-byte key")

    salt = os.urandom(16)
    print(f"Salt: {salt.hex()}")

    # Using the Python API directly
    derived_key = pbkdf2_hmac_sha256(
        password=password,
        salt=salt,
        iterations=100000,
        dklen=32
    )

    print(f"\nDerived key: {derived_key.hex()}")
    print(f"Key length: {len(derived_key)} bytes")

    # Key hierarchy example
    print("\nCreating key hierarchy from derived key...")

    encryption_key = derive_key(derived_key, "database_encryption", 32)
    auth_key = derive_key(derived_key, "api_authentication", 32)
    backup_key = derive_key(derived_key, "backup_encryption", 32)

    print("Derived subkeys:")
    print(f"  Encryption: {encryption_key.hex()[:16]}...")
    print(f"  Authentication: {auth_key.hex()[:16]}...")
    print(f"  Backup: {backup_key.hex()[:16]}...")

    # Verify they're all different
    keys = [encryption_key, auth_key, backup_key]
    unique = len(set(k.hex() for k in keys))

    if unique == 3:
        print("✅ All derived keys are unique (as expected)")
    else:
        print(f"❌ Only {unique} unique keys out of 3")

    # Using CLI
    print("\nUsing CLI for key derivation...")
    result = subprocess.run([
        'cryptocore', 'derive',
        '--password', password,
        '--salt', salt.hex(),
        '--iterations', '100000',
        '--length', '32'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        cli_key_hex = result.stdout.strip().split()[0]
        cli_key = bytes.fromhex(cli_key_hex)

        if cli_key == derived_key:
            print("✅ CLI and API produce same key")
        else:
            print("❌ CLI and API produce different keys")
    else:
        print(f"CLI failed: {result.stderr}")


def example_performance():

    print("\n" + "=" * 60)
    print("Example 6: Performance Measurements")
    print("=" * 60)

    import time

    # Test different PBKDF2 iteration counts
    print("\nPBKDF2 Performance with Different Iterations:")
    print("-" * 40)

    iteration_counts = [1000, 10000, 100000, 500000]

    for iterations in iteration_counts:
        start = time.time()

        # Small test to measure per-iteration time
        pbkdf2_hmac_sha256(
            password="test",
            salt=b"testsalt",
            iterations=iterations,
            dklen=32
        )

        elapsed = time.time() - start
        time_per_iteration = elapsed / iterations * 1000000  # microseconds

        print(f"{iterations:7,} iterations: {elapsed:6.3f}s "
              f"({time_per_iteration:5.1f} µs/iteration)")

    # Hash performance
    print("\nHash Performance (1MB data):")
    print("-" * 40)

    from src.cryptocore.hash import SHA256, SHA3_256

    test_data = b"x" * (1024 * 1024)  # 1MB

    # SHA-256
    start = time.time()
    sha256_hash = SHA256().hash_hex(test_data)
    sha256_time = time.time() - start

    # SHA3-256
    start = time.time()
    sha3_hash = SHA3_256().hash_hex(test_data)
    sha3_time = time.time() - start

    print(f"SHA-256:    {sha256_time:.3f}s ({1 / sha256_time:.1f} MB/s)")
    print(f"SHA3-256:   {sha3_time:.3f}s ({1 / sha3_time:.1f} MB/s)")
    print(f"SHA-256 hash:   {sha256_hash[:16]}...")
    print(f"SHA3-256 hash:  {sha3_hash[:16]}...")

    print("\nNote: These are educational implementations.")
    print("Production libraries (OpenSSL, etc.) are much faster.")


def main():

    print("CryptoCore Usage Examples")
    print("=" * 60)
    print()

    examples = [
        example_encryption,
        example_authenticated_encryption,
        example_hashing,
        example_hmac,
        example_key_derivation,
        example_performance,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            print()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)

    # Show quick reference
    print("\nQuick Reference:")
    print("-" * 40)
    print("Encrypt:    cryptocore --algorithm aes --mode MODE --encrypt --key KEY --input IN --output OUT")
    print("Decrypt:    cryptocore --algorithm aes --mode MODE --decrypt --key KEY --input IN --output OUT")
    print("Hash:       cryptocore dgst --algorithm ALGO --input FILE")
    print("HMAC:       cryptocore dgst --algorithm ALGO --hmac --key KEY --input FILE")
    print("Derive key: cryptocore derive --password PASS --salt SALT --iterations N --length L")


if __name__ == "__main__":
    main()