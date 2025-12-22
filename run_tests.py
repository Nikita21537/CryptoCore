import subprocess
import sys
import os


def run_test(test_file, test_name=None):

    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    if test_name:
        cmd.extend(["-k", test_name])

    print(f"\n{'=' * 60}")
    print(f"Running: {' '.join(cmd)}")
    print('=' * 60)

    result = subprocess.run(cmd)
    return result.returncode == 0


def main():

    print("CryptoCore Sprint 7 - Test Suite")
    print("=" * 60)

    tests = [
        ("tests/test_kdf.py", None),
        ("tests/test_kdf.py", "TestPBKDF2"),
        ("tests/test_kdf.py", "TestHKDF"),
        ("tests/test_kdf.py", "TestCLIDerive"),
        ("tests/test_hash.py", None),
        ("tests/test_csprng.py", None),
        ("tests/test_hmac.py", None),
        ("tests/test_gcm.py", None),
        ("tests/test_encrypt_then_mac.py", None),
        ("tests/test_modes.py", None),
        ("tests/test_cryptocore.py", None),
    ]

    passed = 0
    failed = 0

    for test_file, test_name in tests:
        if not os.path.exists(test_file):
            print(f"Warning: Test file not found: {test_file}")
            continue

        if run_test(test_file, test_name):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Summary:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! ")
        sys.exit(0)


if __name__ == "__main__":
    main()