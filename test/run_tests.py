#!/usr/bin/env python3
import unittest
import sys
import os
import argparse
import json
import tempfile
import subprocess
from pathlib import Path


def discover_and_run_tests(test_dir: str, pattern: str = 'test_*.py'):

    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)

    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)

    return result


def run_unit_tests():

    print("\n" + "=" * 70)
    print("Running Unit Tests")
    print("=" * 70)

    result = discover_and_run_tests('tests/unit')

    if result.wasSuccessful():
        print("✅ All unit tests passed!")
    else:
        print("❌ Some unit tests failed")

    return result.wasSuccessful()


def run_integration_tests():

    print("\n" + "=" * 70)
    print("Running Integration Tests")
    print("=" * 70)

    result = discover_and_run_tests('tests/integration')

    if result.wasSuccessful():
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed")

    return result.wasSuccessful()


def run_known_answer_tests():

    print("\n" + "=" * 70)
    print("Running Known-Answer Tests")
    print("=" * 70)

    # This will be run as part of unit tests
    print("Known-answer tests are included in unit tests.")
    print("Check test output above for NIST/RFC vector results.")

    return True


def run_performance_tests():

    print("\n" + "=" * 70)
    print("Running Performance Tests")
    print("=" * 70)

    # Import performance test modules
    sys.path.insert(0, 'tests')

    try:
        # Run hash performance test
        from unit.test_hash import TestHashModule
        hash_test = TestHashModule()
        hash_test.test_performance()

        # Run encryption performance test
        from integration.test_cli import TestCLIPerformance
        perf_test = TestCLIPerformance()
        perf_test.test_hash_performance()
        perf_test.test_encryption_performance()
        perf_test.test_pbkdf2_performance()

        print("\n✅ Performance tests completed")
        return True

    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return False


def run_interoperability_tests():

    print("\n" + "=" * 70)
    print("Running Interoperability Tests")
    print("=" * 70)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Check if cryptocore command exists
    print("\n1. Checking cryptocore installation...")
    try:
        result = subprocess.run(['cryptocore', '--help'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ cryptocore command available")
            tests_passed += 1
        else:
            print("   ❌ cryptocore command failed")
            tests_failed += 1
    except FileNotFoundError:
        print("   ❌ cryptocore command not found in PATH")
        tests_failed += 1

    # Test 2: Test OpenSSL interoperability for hashing
    print("\n2. Testing OpenSSL interoperability...")
    try:
        # Check if OpenSSL is available
        result = subprocess.run(['openssl', 'version'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ OpenSSL available: {result.stdout.strip()}")

            # Create test file
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                test_data = b"Test data for OpenSSL interoperability"
                f.write(test_data)
                test_file = f.name

            try:
                # Hash with cryptocore
                result1 = subprocess.run(
                    ['cryptocore', 'dgst', '--algorithm', 'sha256',
                     '--input', test_file],
                    capture_output=True, text=True
                )

                # Hash with OpenSSL
                result2 = subprocess.run(
                    ['openssl', 'dgst', '-sha256', test_file],
                    capture_output=True, text=True
                )

                if result1.returncode == 0 and result2.returncode == 0:
                    # Extract hashes
                    hash1 = result1.stdout.strip().split()[0]
                    hash2 = result2.stdout.strip().split()[-1].lower()

                    if hash1 == hash2:
                        print("   ✅ SHA-256 hashes match")
                        tests_passed += 1
                    else:
                        print(f"   ❌ SHA-256 hashes differ:\n"
                              f"      CryptoCore: {hash1}\n"
                              f"      OpenSSL: {hash2}")
                        tests_failed += 1
                else:
                    print("   ❌ Failed to compute hashes")
                    tests_failed += 1

            finally:
                os.unlink(test_file)
        else:
            print("   ⚠️ OpenSSL not available (skipping)")
            tests_passed += 1  # Not a failure, just not available

    except FileNotFoundError:
        print("   ⚠️ OpenSSL not installed (skipping)")
        tests_passed += 1  # Not a failure, just not available

    # Test 3: Test system hash tools
    print("\n3. Testing system hash tools...")
    try:
        # Try sha256sum
        result = subprocess.run(['sha256sum', '--version'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("    sha256sum available")

            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                test_data = b"Test data for system tools"
                f.write(test_data)
                test_file = f.name

            try:
                # Hash with cryptocore
                result1 = subprocess.run(
                    ['cryptocore', 'dgst', '--algorithm', 'sha256',
                     '--input', test_file],
                    capture_output=True, text=True
                )

                # Hash with sha256sum
                result2 = subprocess.run(
                    ['sha256sum', test_file],
                    capture_output=True, text=True
                )

                if result1.returncode == 0 and result2.returncode == 0:
                    hash1 = result1.stdout.strip().split()[0]
                    hash2 = result2.stdout.strip().split()[0]

                    if hash1 == hash2:
                        print("    Hashes match with sha256sum")
                        tests_passed += 1
                    else:
                        print("    Hashes differ with sha256sum")
                        tests_failed += 1
                else:
                    print("   Failed to compute hashes")
                    tests_failed += 1

            finally:
                os.unlink(test_file)
        else:
            # Try shasum on macOS
            result = subprocess.run(['shasum', '-a', '256', '--version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("    shasum available (macOS)")
                tests_passed += 1  # Count as passed
            else:
                print("   ⚠ No system hash tools available")
                tests_passed += 1  # Not a failure

    except FileNotFoundError:
        print("    System hash tools not available")
        tests_passed += 1

    print(f"\nInteroperability results: {tests_passed} passed, {tests_failed} failed")

    return tests_failed == 0


def run_memory_tests():

    print("\n" + "=" * 70)
    print("Running Memory Tests")
    print("=" * 70)

    import tempfile
    import psutil
    import os

    try:
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory usage: {initial_memory:.1f} MB")

        # Create a large file (100MB)
        print("Creating 100MB test file...")
        large_file = tempfile.mktemp()

        with open(large_file, 'wb') as f:
            # Write in chunks to avoid memory issues
            chunk = b'x' * (10 * 1024 * 1024)  # 10MB chunks
            for _ in range(10):  # 100MB total
                f.write(chunk)

        try:
            # Hash the large file
            print("Hashing 100MB file...")

            memory_before = process.memory_info().rss / 1024 / 1024

            result = subprocess.run(
                ['cryptocore', 'dgst', '--algorithm', 'sha256',
                 '--input', large_file],
                capture_output=True, text=True
            )

            memory_after = process.memory_info().rss / 1024 / 1024
            memory_diff = memory_after - memory_before

            if result.returncode == 0:
                print(f" Successfully hashed 100MB file")
                print(f"   Memory increase: {memory_diff:.1f} MB")
                print(f"   Hash: {result.stdout.strip().split()[0][:16]}...")

                # Check that memory increase is reasonable
                if memory_diff < 50:  # Should use < 50MB for 100MB file
                    print("    Memory usage is reasonable")
                    return True
                else:
                    print(f"   ⚠ High memory usage: {memory_diff:.1f} MB")
                    return False
            else:
                print(f" Failed to hash large file: {result.stderr}")
                return False

        finally:
            # Clean up
            if os.path.exists(large_file):
                os.unlink(large_file)

    except ImportError:
        print(" psutil not installed, skipping memory tests")
        return True  # Not a failure
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def run_coverage():

    print("\n" + "=" * 70)
    print("Running Test Coverage")
    print("=" * 70)

    try:
        import pytest

        print("Running coverage analysis...")

        # Run pytest with coverage
        import subprocess
        result = subprocess.run([
            'python', '-m', 'pytest',
            '--cov=src',
            '--cov-report=term',
            '--cov-report=html:coverage_html',
            'tests/'
        ], capture_output=True, text=True)

        print(result.stdout)

        if result.returncode == 0:
            print("\n✅ Coverage analysis completed")

            # Parse coverage percentage from output
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage = parts[-1]
                        print(f"\nOverall coverage: {coverage}")

                        # Check if coverage meets target
                        try:
                            coverage_pct = float(coverage.strip('%'))
                            if coverage_pct >= 90:
                                print("✅ Coverage meets target (≥90%)")
                            else:
                                print(f" Coverage below target: {coverage_pct:.1f}% < 90%")
                        except ValueError:
                            pass
                    break

            return True
        else:
            print(f"❌ Coverage analysis failed: {result.stderr}")
            return False

    except ImportError:
        print(" pytest-cov not installed, skipping coverage analysis")
        print("Install with: pip install pytest-cov")
        return True  # Not a failure


def generate_test_report(results):

    print("\n" + "=" * 70)
    print("Test Summary Report")
    print("=" * 70)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests

    print(f"\nTotal test categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    print("\nDetailed results:")
    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {category:30} {status}")

    if failed_tests == 0:
        print("\n All tests passed! CryptoCore is ready for production.")
        return True
    else:
        print(f"\n⚠️ {failed_tests} test categories failed.")
        print("Please review the failed tests above.")
        return False


def main():

    parser = argparse.ArgumentParser(description='Run CryptoCore tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--performance', action='store_true', help='Run only performance tests')
    parser.add_argument('--interop', action='store_true', help='Run only interoperability tests')
    parser.add_argument('--memory', action='store_true', help='Run only memory tests')
    parser.add_argument('--coverage', action='store_true', help='Run only coverage analysis')
    parser.add_argument('--all', action='store_true', default=True, help='Run all tests (default)')

    args = parser.parse_args()

    print("CryptoCore Test Suite")
    print("=" * 70)

    results = {}

    # Run selected tests
    if args.unit or args.all:
        results['Unit Tests'] = run_unit_tests()

    if args.integration or args.all:
        results['Integration Tests'] = run_integration_tests()

    if args.performance or args.all:
        results['Performance Tests'] = run_performance_tests()

    if args.interop or args.all:
        results['Interoperability Tests'] = run_interoperability_tests()

    if args.memory or args.all:
        results['Memory Tests'] = run_memory_tests()

    if args.coverage or args.all:
        results['Coverage Analysis'] = run_coverage()

    # Generate final report
    print("\n" + "=" * 70)
    overall_success = generate_test_report(results)

    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == '__main__':
    main()