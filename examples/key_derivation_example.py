import os
import sys
import tempfile
import subprocess


def example_1_basic_derivation():

    print("=" * 60)
    print("Example 1: Basic Key Derivation")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "src.cryptocore", "derive",
        "--password", "MySecureDatabasePassword!2024",
        "--salt", "a1b2c3d4e5f67890fedcba9876543210",
        "--iterations", "100000",
        "--length", "32"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Command: {' '.join(cmd[2:])}")
    print(f"Output: {result.stdout.strip()}")
    print()


def example_2_auto_salt():

    print("=" * 60)
    print("Example 2: Auto-generated Salt")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "src.cryptocore", "derive",
        "--password", "ApplicationSecretKey",
        "--iterations", "500000",
        "--length", "16",
        "--output", "derived_key.txt"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Command: {' '.join(cmd[2:])}")
    print(f"Output preview:\n{result.stdout[:100]}...")

    if os.path.exists("derived_key.txt"):
        with open("derived_key.txt", "r") as f:
            content = f.read()
        print(f"File content: {content.strip()}")
        os.remove("derived_key.txt")
    print()


def example_3_rfc_test_vector():

    print("=" * 60)
    print("Example 3: RFC 6070 Test Vector")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "src.cryptocore", "derive",
        "--password", "password",
        "--salt", "73616c74",  # "salt" in hex
        "--iterations", "1",
        "--length", "20"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Command: {' '.join(cmd[2:])}")
    print(f"Output: {result.stdout.strip()}")

    key_hex = result.stdout.strip().split()[0]
    expected = "0c60c80f961f0e71f3a9b524af6012062fe037a6"

    if key_hex == expected:
        print("✓ Matches RFC 6070 test vector!")
    else:
        print(f"✗ Doesn't match. Expected: {expected}")
    print()


def example_4_key_hierarchy():

    print("=" * 60)
    print("Example 4: Key Hierarchy")
    print("=" * 60)

    # First derive a master key
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        output_file = f.name

    try:
        cmd = [
            sys.executable, "-m", "src.cryptocore", "derive",
            "--password", "MasterPasswordForApp",
            "--iterations", "100000",
            "--length", "32",
            "--output", output_file
        ]

        subprocess.run(cmd, capture_output=True, text=True)

        with open(output_file, "r") as f:
            master_key_hex = f.read().strip().split()[0]

        master_key = bytes.fromhex(master_key_hex)

        # Now demonstrate key hierarchy
        from src.cryptocore.kdf import derive_key

        print("Master Key:", master_key_hex)
        print()

        # Derive different keys for different purposes
        encryption_key = derive_key(master_key, "database_encryption", 32)
        auth_key = derive_key(master_key, "api_authentication", 32)
        signing_key = derive_key(master_key, "jwt_signing", 32)

        print("Derived Keys:")
        print(f"  Encryption: {encryption_key.hex()[:16]}...")
        print(f"  Authentication: {auth_key.hex()[:16]}...")
        print(f"  Signing: {signing_key.hex()[:16]}...")
        print()

        # Verify they're all different
        keys = [encryption_key, auth_key, signing_key]
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if keys[i] == keys[j]:
                    print(f"✗ Keys {i} and {j} are the same (should be different)")
                else:
                    print(f"✓ Keys {i} and {j} are different (correct)")

    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

    print()


def example_5_performance():

    print("=" * 60)
    print("Example 5: Performance Comparison")
    print("=" * 60)

    import time

    iterations_list = [1000, 10000, 100000, 500000]

    for iterations in iterations_list:
        start_time = time.time()

        cmd = [
            sys.executable, "-m", "src.cryptocore", "derive",
            "--password", "test",
            "--salt", "1234567890abcdef",
            "--iterations", str(iterations),
            "--length", "32"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"{iterations:7,} iterations: {elapsed:6.3f} seconds")
        else:
            print(f"{iterations:7,} iterations: FAILED")

    print()
    print("Note: Higher iterations = better security but slower derivation")
    print()


def main():

    print("CryptoCore Key Derivation Examples")
    print("=" * 60)
    print()

    examples = [
        example_1_basic_derivation,
        example_2_auto_salt,
        example_3_rfc_test_vector,
        example_4_key_hierarchy,
        example_5_performance,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"Example {i} failed: {e}")
            print()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()