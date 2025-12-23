import unittest
import tempfile
import os
import subprocess
import sys
from src.hash import SHA256, SHA3_256, hash_data_hex, hash_file


class TestSHA256(unittest.TestCase):


    def setUp(self):
        self.sha256 = SHA256()

    def test_empty_string(self):

        result = self.sha256.hash_hex(b"")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(result, expected, f"Empty string hash mismatch")

    def test_abc(self):

        result = self.sha256.hash_hex(b"abc")
        expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        self.assertEqual(result, expected, f"'abc' hash mismatch")

    def test_long_string(self):

        data = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
        result = self.sha256.hash_hex(data)
        expected = "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
        self.assertEqual(result, expected, f"Long string hash mismatch")

    def test_padding(self):


        test_cases = [
            (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            (b"a", "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"),
            (b"ab", "fb8e20fc2e4c3f248c60c39bd652f3c1347298bb977b8b4d5903b85055620603"),
            (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
            (b"abcd", "88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589"),
        ]

        for data, expected in test_cases:
            result = self.sha256.hash_hex(data)
            self.assertEqual(result, expected, f"Hash mismatch for data: {data}")

    def test_incremental_hashing(self):

        data1 = b"Hello, "
        data2 = b"World!"
        full_data = b"Hello, World!"


        self.sha256.update(data1)
        self.sha256.update(data2)
        incremental_hash = self.sha256.hexdigest()


        full_hash = SHA256().hash_hex(full_data)

        self.assertEqual(incremental_hash, full_hash, "Incremental hashing failed")

    def test_avalanche_effect(self):

        data1 = b"Hello, world!"
        data2 = b"Hello, world?"

        hash1 = SHA256().hash_hex(data1)
        hash2 = SHA256().hash_hex(data2)


        bin1 = bin(int(hash1, 16))[2:].zfill(256)
        bin2 = bin(int(hash2, 16))[2:].zfill(256)

        diff_count = sum(bit1 != bit2 for bit1, bit2 in zip(bin1, bin2))


        self.assertGreater(diff_count, 100, f"Weak avalanche effect: only {diff_count} bits changed")
        self.assertLess(diff_count, 156, f"Weak avalanche effect: {diff_count} bits changed")

        print(f"✓ Avalanche effect: {diff_count}/256 bits changed (~{diff_count / 256 * 100:.1f}%)")

    def test_large_data(self):

        large_data = b"A" * (1024 * 1024)  # 1MB


        hash_value = SHA256().hash_hex(large_data)


        self.assertEqual(len(hash_value), 64, "Invalid hash length")
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_value), "Invalid hex characters")

        print(f"✓ Large data hash: {hash_value[:16]}...")


class TestSHA3_256(unittest.TestCase):


    def test_empty_string(self):

        result = SHA3_256().hash_hex(b"")
        expected = "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
        self.assertEqual(result, expected, f"Empty string SHA3-256 hash mismatch")

    def test_abc(self):

        result = SHA3_256().hash_hex(b"abc")
        expected = "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"
        self.assertEqual(result, expected, f"'abc' SHA3-256 hash mismatch")

    def test_incremental_hashing(self):

        data1 = b"Hello, "
        data2 = b"World!"
        full_data = b"Hello, World!"


        sha3 = SHA3_256()
        sha3.update(data1)
        sha3.update(data2)
        incremental_hash = sha3.hexdigest()


        full_hash = SHA3_256().hash_hex(full_data)

        self.assertEqual(incremental_hash, full_hash, "SHA3-256 incremental hashing failed")


class TestHashModule(unittest.TestCase):


    def test_hash_data(self):

        data = b"test data"


        sha256_hash = hash_data_hex(data, 'sha256')
        self.assertEqual(len(sha256_hash), 64)


        sha3_hash = hash_data_hex(data, 'sha3-256')
        self.assertEqual(len(sha3_hash), 64)


        self.assertNotEqual(sha256_hash, sha3_hash)

    def test_hash_file(self):


        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"This is a test file for hashing.")
            temp_file = f.name

        try:

            sha256_hash = hash_file(temp_file, 'sha256')
            sha3_hash = hash_file(temp_file, 'sha3-256')


            self.assertEqual(len(sha256_hash), 64)
            self.assertEqual(len(sha3_hash), 64)


            with open(temp_file, 'rb') as f:
                data = f.read()

            direct_sha256 = hash_data_hex(data, 'sha256')
            direct_sha3 = hash_data_hex(data, 'sha3-256')

            self.assertEqual(sha256_hash, direct_sha256)
            self.assertEqual(sha3_hash, direct_sha3)

        finally:
            os.remove(temp_file)


class TestNISTVectors(unittest.TestCase):


    def test_sha256_nist_vectors(self):


        test_vectors = [
            ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
            ("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
             "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
            (
            "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu",
            "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1"),
        ]

        for message, expected in test_vectors:
            result = SHA256().hash_hex(message.encode('ascii'))
            self.assertEqual(result, expected,
                             f"SHA-256 mismatch for message: '{message[:20]}...'")

        print(f"✓ Passed {len(test_vectors)} NIST test vectors")

    def test_sha3_256_nist_vectors(self):


        test_vectors = [
            ("", "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
            ("abc", "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"),
            ("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
             "41c0dba2a9d6240849100376a8235e2c82e1b9998a999e21db32dd97496d3376"),
        ]

        for message, expected in test_vectors:
            result = SHA3_256().hash_hex(message.encode('ascii'))
            self.assertEqual(result, expected,
                             f"SHA3-256 mismatch for message: '{message[:20]}...'")

        print(f"✓ Passed {len(test_vectors)} SHA3-256 test vectors")


class TestCLIHash(unittest.TestCase):


    def test_cli_sha256(self):

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Hello, CryptoCore!"
            f.write(test_content)
            test_file = f.name

        hash_file = test_file + '.hash'

        try:

            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--input", test_file,
                    "--output", hash_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0,
                             f"CLI failed: {result.stderr}")


            with open(hash_file, 'r') as f:
                hash_line = f.read().strip()


            hash_value, filename = hash_line.split()
            self.assertEqual(filename, test_file)


            expected_hash = SHA256().hash_hex(test_content)
            self.assertEqual(hash_value, expected_hash)

            print(f"✓ CLI SHA-256 test passed: {hash_value[:16]}...")

        finally:

            for file_path in [test_file, hash_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    def test_cli_sha3_256(self):


        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Test data for SHA3"
            f.write(test_content)
            test_file = f.name

        try:

            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha3-256",
                    "--input", test_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0,
                             f"CLI failed: {result.stderr}")


            output_lines = result.stdout.strip().split('\n')
            hash_line = output_lines[-1]  # Last line contains hash

            hash_value, filename = hash_line.split()
            self.assertEqual(filename, test_file)


            expected_hash = SHA3_256().hash_hex(test_content)
            self.assertEqual(hash_value, expected_hash)

            print(f"✓ CLI SHA3-256 test passed: {hash_value[:16]}...")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_interoperability_with_system_tools(self):


        if sys.platform == 'win32':
            self.skipTest("System hash tools not reliably available on Windows")


        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:

            import random
            test_data = bytes(random.getrandbits(8) for _ in range(1024))
            f.write(test_data)
            test_file = f.name

        try:

            our_result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--input", test_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )


            system_result = subprocess.run(
                ["sha256sum", test_file],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if system_result.returncode != 0:

                system_result = subprocess.run(
                    ["shasum", "-a", "256", test_file],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )

            if system_result.returncode == 0:

                our_hash = our_result.stdout.strip().split()[0]
                system_hash = system_result.stdout.strip().split()[0]

                self.assertEqual(our_hash, system_hash,
                                 f"Interoperability failed: {our_hash} != {system_hash}")
                print(f"✓ Interoperability with system tools verified")
            else:
                print("Note: System hash tools not available for interoperability test")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':

    unittest.main()
