import unittest
import os
import sys
import json
import hashlib

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.hash import SHA256, SHA3_256, hash_data_hex


class TestSHA256(unittest.TestCase):


    def setUp(self):
        self.sha256 = SHA256()

    def test_nist_vectors(self):

        vectors_path = os.path.join(
            os.path.dirname(__file__), '../vectors/nist_sha256.json'
        )

        if not os.path.exists(vectors_path):
            self.skipTest("NIST test vectors not found")

        with open(vectors_path, 'r') as f:
            vectors = json.load(f)

        for i, vector in enumerate(vectors):
            with self.subTest(vector=i):
                message = bytes.fromhex(vector['message'])
                expected = vector['hash']

                result = SHA256().hash_hex(message)
                self.assertEqual(result, expected,
                                 f"Vector {i} failed: {vector['description']}")

        print(f"✓ Passed {len(vectors)} NIST SHA-256 test vectors")

    def test_empty_string(self):

        result = self.sha256.hash_hex(b"")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(result, expected)

    def test_abc(self):

        result = self.sha256.hash_hex(b"abc")
        expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        self.assertEqual(result, expected)

    def test_long_string(self):

        data = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
        result = self.sha256.hash_hex(data)
        expected = "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
        self.assertEqual(result, expected)

    def test_incremental_hashing(self):

        data1 = b"Hello, "
        data2 = b"World!"
        full_data = b"Hello, World!"

        # Incremental
        self.sha256.update(data1)
        self.sha256.update(data2)
        incremental_hash = self.sha256.hexdigest()

        # One-shot
        full_hash = SHA256().hash_hex(full_data)

        self.assertEqual(incremental_hash, full_hash)

    def test_reset(self):

        data1 = b"First message"
        data2 = b"Second message"

        # Hash first message
        hash1 = SHA256().hash_hex(data1)

        # Use same instance for second message
        hasher = SHA256()
        hasher.update(data1)
        hasher.reset()  # Reset

        hasher.update(data2)
        hash2 = hasher.hexdigest()

        # Should match fresh hash of second message
        expected = SHA256().hash_hex(data2)
        self.assertEqual(hash2, expected)
        self.assertNotEqual(hash1, hash2)

    def test_avalanche_effect(self):

        data1 = b"Hello, world!"
        data2 = b"Hello, world?"

        hash1 = SHA256().hash_hex(data1)
        hash2 = SHA256().hash_hex(data2)

        # Convert to binary for bit comparison
        bin1 = bin(int(hash1, 16))[2:].zfill(256)
        bin2 = bin(int(hash2, 16))[2:].zfill(256)

        # Count differing bits
        diff_count = sum(bit1 != bit2 for bit1, bit2 in zip(bin1, bin2))

        # Should be around 50% (128 bits)
        # Allow some variation
        self.assertGreater(diff_count, 100, "Weak avalanche effect")
        self.assertLess(diff_count, 156, "Weak avalanche effect")

        print(f"  Avalanche effect: {diff_count}/256 bits changed "
              f"({diff_count / 256 * 100:.1f}%)")

    def test_large_data(self):

        # 1MB of data
        large_data = b"A" * (1024 * 1024)

        hash_value = SHA256().hash_hex(large_data)

        self.assertEqual(len(hash_value), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_value))

        # Compare with reference implementation
        ref_hash = hashlib.sha256(large_data).hexdigest()
        self.assertEqual(hash_value, ref_hash)

        print(f"  Large data hash: {hash_value[:16]}...")

    def test_various_lengths(self):

        for length in [0, 1, 55, 56, 57, 63, 64, 65, 127, 128, 129, 512, 1000]:
            with self.subTest(length=length):
                data = b"x" * length
                hash_value = SHA256().hash_hex(data)

                self.assertEqual(len(hash_value), 64)

                # Compare with reference
                ref_hash = hashlib.sha256(data).hexdigest()
                self.assertEqual(hash_value, ref_hash)

    def test_unicode(self):

        test_cases = [
            "Hello, World!",
            "Привет, мир!",
            "",
            "Test with emoji ",
            "Mixed: 测试 123!",
        ]

        for text in test_cases:
            with self.subTest(text=text[:20]):
                data = text.encode('utf-8')
                hash_value = SHA256().hash_hex(data)

                # Compare with reference
                ref_hash = hashlib.sha256(data).hexdigest()
                self.assertEqual(hash_value, ref_hash)


class TestSHA3_256(unittest.TestCase):


    def test_nist_vectors(self):

        vectors_path = os.path.join(
            os.path.dirname(__file__), '../vectors/nist_sha3_256.json'
        )

        if not os.path.exists(vectors_path):
            self.skipTest("NIST SHA3-256 test vectors not found")

        with open(vectors_path, 'r') as f:
            vectors = json.load(f)

        for i, vector in enumerate(vectors):
            with self.subTest(vector=i):
                message = bytes.fromhex(vector['message'])
                expected = vector['hash']

                result = SHA3_256().hash_hex(message)
                self.assertEqual(result, expected,
                                 f"Vector {i} failed")

        print(f"✓ Passed {len(vectors)} NIST SHA3-256 test vectors")

    def test_empty_string(self):

        result = SHA3_256().hash_hex(b"")
        expected = "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
        self.assertEqual(result, expected)

    def test_abc(self):

        result = SHA3_256().hash_hex(b"abc")
        expected = "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"
        self.assertEqual(result, expected)

    def test_incremental_hashing(self):

        data1 = b"Hello, "
        data2 = b"World!"
        full_data = b"Hello, World!"

        # Incremental
        sha3 = SHA3_256()
        sha3.update(data1)
        sha3.update(data2)
        incremental_hash = sha3.hexdigest()

        # One-shot
        full_hash = SHA3_256().hash_hex(full_data)

        self.assertEqual(incremental_hash, full_hash)

    def test_avalanche_effect(self):

        data1 = b"Test message 1"
        data2 = b"Test message 2"

        hash1 = SHA3_256().hash_hex(data1)
        hash2 = SHA3_256().hash_hex(data2)

        self.assertNotEqual(hash1, hash2)

        # Check they're substantially different
        bin1 = bin(int(hash1, 16))[2:].zfill(256)
        bin2 = bin(int(hash2, 16))[2:].zfill(256)

        diff_count = sum(bit1 != bit2 for bit1, bit2 in zip(bin1, bin2))

        self.assertGreater(diff_count, 100)
        print(f"  SHA3-256 avalanche: {diff_count}/256 bits changed")


class TestHashModule(unittest.TestCase):


    def test_hash_data_hex(self):

        data = b"test data"

        # SHA-256
        sha256_hash = hash_data_hex(data, 'sha256')
        self.assertEqual(len(sha256_hash), 64)

        # SHA3-256
        sha3_hash = hash_data_hex(data, 'sha3-256')
        self.assertEqual(len(sha3_hash), 64)

        # Should be different
        self.assertNotEqual(sha256_hash, sha3_hash)

        # Invalid algorithm
        with self.assertRaises(ValueError):
            hash_data_hex(data, 'invalid')

    def test_consistency(self):

        data = b"Consistency test data"

        # Method 1: One-shot
        hash1 = SHA256().hash_hex(data)

        # Method 2: Using hash_data_hex
        hash2 = hash_data_hex(data, 'sha256')

        # Method 3: Incremental
        hasher = SHA256()
        for i in range(0, len(data), 3):
            hasher.update(data[i:i + 3])
        hash3 = hasher.hexdigest()

        # All should be equal
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, hash3)

    def test_performance(self):

        import time

        data = b"x" * (1024 * 1024)  # 1MB

        algorithms = ['sha256', 'sha3-256']

        for algo in algorithms:
            start = time.time()

            if algo == 'sha256':
                hasher = SHA256()
            else:
                hasher = SHA3_256()

            # Process in chunks (simulating file processing)
            chunk_size = 8192
            for i in range(0, len(data), chunk_size):
                hasher.update(data[i:i + chunk_size])

            hash_value = hasher.hexdigest()
            elapsed = time.time() - start

            print(f"  {algo}: {elapsed:.3f}s for 1MB ({len(data) / elapsed / 1024 / 1024:.1f} MB/s)")

            # Verify it produced output
            self.assertEqual(len(hash_value), 64)


class TestInteroperability(unittest.TestCase):


    def test_openssl_interoperability(self):

        # Skip if OpenSSL not available
        import subprocess
        try:
            subprocess.run(['openssl', 'version'],
                           capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("OpenSSL not available")

        test_data = b"Test data for OpenSSL interoperability"

        # Our hash
        our_hash = SHA256().hash_hex(test_data)

        # OpenSSL hash
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb') as f:
            f.write(test_data)
            f.flush()

            result = subprocess.run(
                ['openssl', 'dgst', '-sha256', f.name],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                openssl_hash = result.stdout.strip().split()[-1]
                self.assertEqual(our_hash, openssl_hash.lower())
                print("✓ OpenSSL interoperability verified")
            else:
                # Try alternative command
                result = subprocess.run(
                    ['openssl', 'sha256', f.name],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    openssl_hash = result.stdout.strip().split()[-1]
                    self.assertEqual(our_hash, openssl_hash.lower())
                    print("✓ OpenSSL interoperability verified")

    def test_hashlib_interoperability(self):

        test_cases = [
            b"",
            b"a",
            b"abc",
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
            b"A" * 1000,
            b"Test with null\0byte",
            b"Unicode: ".encode('utf-8'),
        ]

        for data in test_cases:
            with self.subTest(data=data[:20]):
                # SHA-256
                our_hash = SHA256().hash_hex(data)
                ref_hash = hashlib.sha256(data).hexdigest()
                self.assertEqual(our_hash, ref_hash)

                # SHA3-256 (Python 3.6+)
                if hasattr(hashlib, 'sha3_256'):
                    our_hash = SHA3_256().hash_hex(data)
                    ref_hash = hashlib.sha3_256(data).hexdigest()
                    self.assertEqual(our_hash, ref_hash)


if __name__ == '__main__':

    unittest.main()
