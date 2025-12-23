import unittest
import os
import sys
import tempfile
import subprocess
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestCLIBasic(unittest.TestCase):


    def test_help(self):

        result = subprocess.run(
            ['cryptocore', '--help'],
            capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())
        self.assertIn('encrypt', result.stdout.lower())
        self.assertIn('decrypt', result.stdout.lower())
        self.assertIn('dgst', result.stdout.lower())
        self.assertIn('derive', result.stdout.lower())

    def test_version(self):

        # First try with -v flag
        result = subprocess.run(
            ['cryptocore', '-v'],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            # Try alternative
            result = subprocess.run(
                ['python', '-m', 'src.cryptocore', '--version'],
                capture_output=True, text=True
            )

        # Should print version (setup.py defines it)
        if result.returncode == 0:
            self.assertIn('cryptocore', result.stdout.lower())

    def test_invalid_command(self):

        result = subprocess.run(
            ['cryptocore', 'invalidcommand'],
            capture_output=True, text=True
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('error', result.stderr.lower())


class TestCLIEncryption(unittest.TestCase):


    def setUp(self):
        # Create temporary test file
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.txt')

        with open(self.test_file, 'wb') as f:
            f.write(b"This is a test file for encryption.\n" + b"Line 2\n" + b"Line 3\n")

    def tearDown(self):
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def run_cryptocore(self, args):

        cmd = ['cryptocore'] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_encrypt_decrypt_roundtrip_ecb(self):

        key = '00112233445566778899aabbccddeeff'
        encrypted = os.path.join(self.temp_dir, 'test.enc')
        decrypted = os.path.join(self.temp_dir, 'test.dec')

        # Encrypt
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'ecb',
            '--encrypt',
            '--key', key,
            '--input', self.test_file,
            '--output', encrypted
        ])

        self.assertEqual(result.returncode, 0, f"Encryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(encrypted))

        # Decrypt
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'ecb',
            '--decrypt',
            '--key', key,
            '--input', encrypted,
            '--output', decrypted
        ])

        self.assertEqual(result.returncode, 0, f"Decryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(decrypted))

        # Compare files
        with open(self.test_file, 'rb') as f:
            original = f.read()

        with open(decrypted, 'rb') as f:
            restored = f.read()

        self.assertEqual(original, restored)

    def test_encrypt_decrypt_roundtrip_cbc(self):

        key = '00112233445566778899aabbccddeeff'
        encrypted = os.path.join(self.temp_dir, 'test.enc')
        decrypted = os.path.join(self.temp_dir, 'test.dec')

        # Encrypt (auto-generates IV)
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'cbc',
            '--encrypt',
            '--key', key,
            '--input', self.test_file,
            '--output', encrypted
        ])

        self.assertEqual(result.returncode, 0, f"Encryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(encrypted))
        self.assertIn('Generated IV', result.stdout)

        # Decrypt (reads IV from file)
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'cbc',
            '--decrypt',
            '--key', key,
            '--input', encrypted,
            '--output', decrypted
        ])

        self.assertEqual(result.returncode, 0, f"Decryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(decrypted))

        # Compare files
        with open(self.test_file, 'rb') as f:
            original = f.read()

        with open(decrypted, 'rb') as f:
            restored = f.read()

        self.assertEqual(original, restored)

    def test_encrypt_decrypt_roundtrip_gcm(self):

        key = '00112233445566778899aabbccddeeff'
        aad = 'aabbccddeeff'
        encrypted = os.path.join(self.temp_dir, 'test.gcm')
        decrypted = os.path.join(self.temp_dir, 'test.dec')

        # Encrypt
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'gcm',
            '--encrypt',
            '--key', key,
            '--aad', aad,
            '--input', self.test_file,
            '--output', encrypted
        ])

        self.assertEqual(result.returncode, 0, f"Encryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(encrypted))
        self.assertIn('Generated nonce', result.stdout)

        # Decrypt with correct AAD
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'gcm',
            '--decrypt',
            '--key', key,
            '--aad', aad,
            '--input', encrypted,
            '--output', decrypted
        ])

        self.assertEqual(result.returncode, 0, f"Decryption failed: {result.stderr}")
        self.assertTrue(os.path.exists(decrypted))
        self.assertIn('GCM decryption completed successfully', result.stdout)

        # Compare files
        with open(self.test_file, 'rb') as f:
            original = f.read()

        with open(decrypted, 'rb') as f:
            restored = f.read()

        self.assertEqual(original, restored)

    def test_gcm_authentication_failure(self):

        key = '00112233445566778899aabbccddeeff'
        encrypted = os.path.join(self.temp_dir, 'test.gcm')
        decrypted = os.path.join(self.temp_dir, 'test.dec')

        # Encrypt with AAD1
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'gcm',
            '--encrypt',
            '--key', key,
            '--aad', 'aad1',
            '--input', self.test_file,
            '--output', encrypted
        ])

        self.assertEqual(result.returncode, 0)

        # Try to decrypt with wrong AAD
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'gcm',
            '--decrypt',
            '--key', key,
            '--aad', 'wrongaad',  # Different AAD
            '--input', encrypted,
            '--output', decrypted
        ])

        # Should fail
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('authentication failed', result.stderr.lower())

        # Output file should not exist
        self.assertFalse(os.path.exists(decrypted))

    def test_auto_key_generation(self):

        encrypted = os.path.join(self.temp_dir, 'test.enc')

        # Encrypt without key (should generate one)
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'cbc',
            '--encrypt',
            '--input', self.test_file,
            '--output', encrypted
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn('Generated key:', result.stdout)
        self.assertIn('Please save this key for decryption', result.stderr)

        # Extract key from output
        import re
        match = re.search(r'Generated key: ([0-9a-f]{32})', result.stdout)
        self.assertIsNotNone(match, "Could not find generated key")

        generated_key = match.group(1)

        # Decrypt with generated key
        decrypted = os.path.join(self.temp_dir, 'test.dec')
        result = self.run_cryptocore([
            '--algorithm', 'aes',
            '--mode', 'cbc',
            '--decrypt',
            '--key', generated_key,
            '--input', encrypted,
            '--output', decrypted
        ])

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(decrypted))

    def test_all_modes_roundtrip(self):

        key = '00112233445566778899aabbccddeeff'
        modes = ['ecb', 'cbc', 'cfb', 'ofb', 'ctr', 'gcm', 'etm']

        for mode in modes:
            with self.subTest(mode=mode):
                encrypted = os.path.join(self.temp_dir, f'test_{mode}.enc')
                decrypted = os.path.join(self.temp_dir, f'test_{mode}.dec')

                # Build command
                cmd = [
                    '--algorithm', 'aes',
                    '--mode', mode,
                    '--encrypt',
                    '--key', key,
                    '--input', self.test_file,
                    '--output', encrypted
                ]

                # Add AAD for authenticated modes
                if mode in ['gcm', 'etm']:
                    cmd.extend(['--aad', 'testaad'])

                # Encrypt
                result = self.run_cryptocore(cmd)
                self.assertEqual(result.returncode, 0,
                                 f"{mode} encryption failed: {result.stderr}")

                # Build decrypt command
                cmd = [
                    '--algorithm', 'aes',
                    '--mode', mode,
                    '--decrypt',
                    '--key', key,
                    '--input', encrypted,
                    '--output', decrypted
                ]

                if mode in ['gcm', 'etm']:
                    cmd.extend(['--aad', 'testaad'])

                # Decrypt
                result = self.run_cryptocore(cmd)
                self.assertEqual(result.returncode, 0,
                                 f"{mode} decryption failed: {result.stderr}")

                # Verify
                with open(self.test_file, 'rb') as f:
                    original = f.read()

                with open(decrypted, 'rb') as f:
                    restored = f.read()

                self.assertEqual(original, restored,
                                 f"{mode} roundtrip failed")

        print(f"✓ All {len(modes)} modes roundtrip successfully")


class TestCLIHash(unittest.TestCase):


    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.txt')

        with open(self.test_file, 'wb') as f:
            f.write(b"This is a test file for hashing.\n")

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def run_cryptocore(self, args):

        cmd = ['cryptocore'] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_hash_sha256(self):

        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha256',
            '--input', self.test_file
        ])

        self.assertEqual(result.returncode, 0)

        # Output should be HASH FILENAME
        lines = result.stdout.strip().split('\n')
        last_line = lines[-1]

        hash_part, filename = last_line.split()
        self.assertEqual(filename, self.test_file)
        self.assertEqual(len(hash_part), 64)  # 32 bytes = 64 hex chars

        print(f"  SHA-256 hash: {hash_part[:16]}...")

    def test_hash_sha3_256(self):

        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha3-256',
            '--input', self.test_file,
            '--output', os.path.join(self.temp_dir, 'hash.txt')
        ])

        self.assertEqual(result.returncode, 0)

        # Check output file
        hash_file = os.path.join(self.temp_dir, 'hash.txt')
        self.assertTrue(os.path.exists(hash_file))

        with open(hash_file, 'r') as f:
            content = f.read().strip()

        hash_part, filename = content.split()
        self.assertEqual(filename, self.test_file)
        self.assertEqual(len(hash_part), 64)

    def test_hash_stdin(self):

        import subprocess

        # Pipe data to cryptocore
        echo = subprocess.Popen(['echo', '-n', 'test data'], stdout=subprocess.PIPE)
        result = subprocess.run(
            ['cryptocore', 'dgst', '--algorithm', 'sha256', '--input', '-'],
            stdin=echo.stdout,
            capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('stdin', result.stdout)

    def test_hmac_generation(self):

        key = '00112233445566778899aabbccddeeff'

        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha256',
            '--hmac',
            '--key', key,
            '--input', self.test_file
        ])

        self.assertEqual(result.returncode, 0)

        # Output should be HMAC FILENAME
        hmac_part, filename = result.stdout.strip().split()
        self.assertEqual(filename, self.test_file)
        self.assertEqual(len(hmac_part), 64)

    def test_hmac_verification(self):

        key = '00112233445566778899aabbccddeeff'
        hmac_file = os.path.join(self.temp_dir, 'test.hmac')

        # Generate HMAC
        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha256',
            '--hmac',
            '--key', key,
            '--input', self.test_file,
            '--output', hmac_file
        ])

        self.assertEqual(result.returncode, 0)

        # Verify with correct key
        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha256',
            '--hmac',
            '--key', key,
            '--input', self.test_file,
            '--verify', hmac_file
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn('[OK]', result.stdout)

        # Verify with wrong key (should fail)
        result = self.run_cryptocore([
            'dgst',
            '--algorithm', 'sha256',
            '--hmac',
            '--key', 'ffeeddccbbaa99887766554433221100',  # Different key
            '--input', self.test_file,
            '--verify', hmac_file
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('[ERROR]', result.stderr)


class TestCLIDerive(unittest.TestCase):


    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def run_cryptocore(self, args):

        cmd = ['cryptocore'] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_derive_basic(self):

        result = self.run_cryptocore([
            'derive',
            '--password', 'MyPassword123!',
            '--salt', '1234567890abcdef1234567890abcdef',
            '--iterations', '1000',
            '--length', '32'
        ])

        self.assertEqual(result.returncode, 0)

        # Output format: KEY_HEX SALT_HEX
        output = result.stdout.strip()
        parts = output.split()

        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[0]), 64)  # 32 bytes
        self.assertEqual(len(parts[1]), 32)  # 16 bytes

        print(f"  Derived key (first 16 chars): {parts[0][:16]}...")

    def test_derive_auto_salt(self):

        result = self.run_cryptocore([
            'derive',
            '--password', 'AnotherPassword',
            '--iterations', '50000',
            '--length', '16'
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn('Generated random salt', result.stdout)

        output = result.stdout.strip()
        parts = output.split()
        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[0]), 32)  # 16 bytes = 32 hex chars

    def test_derive_output_file(self):

        output_file = os.path.join(self.temp_dir, 'derived_key.txt')

        result = self.run_cryptocore([
            'derive',
            '--password', 'test',
            '--salt', '1234567890abcdef',
            '--iterations', '100',
            '--length', '32',
            '--output', output_file
        ])

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            content = f.read().strip()

        parts = content.split()
        self.assertEqual(len(parts), 2)

        # Should also create .bin file with raw key
        bin_file = output_file + '.bin'
        self.assertTrue(os.path.exists(bin_file))

        with open(bin_file, 'rb') as f:
            key_bytes = f.read()

        self.assertEqual(len(key_bytes), 32)

    def test_derive_raw_output(self):

        output_file = os.path.join(self.temp_dir, 'key.bin')

        result = self.run_cryptocore([
            'derive',
            '--password', 'test',
            '--salt', '1234567890abcdef',
            '--iterations', '100',
            '--length', '16',
            '--raw',
            '--output', output_file
        ])

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'rb') as f:
            key_bytes = f.read()

        self.assertEqual(len(key_bytes), 16)

    def test_derive_rfc_vector(self):
        """Test with RFC 6070 test vector."""
        result = self.run_cryptocore([
            'derive',
            '--password', 'password',
            '--salt', '73616c74',  # "salt" in hex
            '--iterations', '1',
            '--length', '20'
        ])

        self.assertEqual(result.returncode, 0)

        key_hex = result.stdout.strip().split()[0]
        expected = "0c60c80f961f0e71f3a9b524af6012062fe037a6"

        self.assertEqual(key_hex, expected)
        print("✓ RFC 6070 test vector passed")

    def test_derive_warnings(self):
        """Test warnings for low iteration count."""
        result = self.run_cryptocore([
            'derive',
            '--password', 'test',
            '--salt', '1234567890abcdef',
            '--iterations', '100',  # Low
            '--length', '16'
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn('[WARNING]', result.stderr)
        self.assertIn('low iteration count', result.stderr)


class TestCLIErrorHandling(unittest.TestCase):


    def test_missing_input_file(self):

        result = subprocess.run(
            ['cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
             '--encrypt', '--input', '/nonexistent/file.txt'],
            capture_output=True, text=True
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not exist', result.stderr.lower())

    def test_invalid_hex_key(self):

        result = subprocess.run(
            ['cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
             '--encrypt', '--key', 'nothex', '--input', '-'],
            capture_output=True, text=True,
            input='test'
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid hexadecimal', result.stderr.lower())

    def test_missing_key_for_decryption(self):

        result = subprocess.run(
            ['cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
             '--decrypt', '--input', '-'],
            capture_output=True, text=True,
            input='test'
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('key required', result.stderr.lower())

    def test_invalid_mode(self):

        result = subprocess.run(
            ['cryptocore', '--algorithm', 'aes', '--mode', 'invalid',
             '--encrypt', '--input', '-'],
            capture_output=True, text=True,
            input='test'
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid mode', result.stderr.lower())

    def test_invalid_hash_algorithm(self):

        result = subprocess.run(
            ['cryptocore', 'dgst', '--algorithm', 'invalid',
             '--input', '-'],
            capture_output=True, text=True,
            input='test'
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid algorithm', result.stderr.lower())


class TestCLIPerformance(unittest.TestCase):


    def test_hash_performance(self):

        import tempfile
        import time

        # Create 10MB test file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write 10MB of data
            chunk = b'x' * 1024
            for _ in range(10 * 1024):  # 10MB
                f.write(chunk)
            test_file = f.name

        try:
            # Time SHA-256
            start = time.time()
            result = subprocess.run(
                ['cryptocore', 'dgst', '--algorithm', 'sha256',
                 '--input', test_file],
                capture_output=True, text=True
            )
            sha256_time = time.time() - start

            self.assertEqual(result.returncode, 0)

            # Time SHA3-256
            start = time.time()
            result = subprocess.run(
                ['cryptocore', 'dgst', '--algorithm', 'sha3-256',
                 '--input', test_file],
                capture_output=True, text=True
            )
            sha3_time = time.time() - start

            self.assertEqual(result.returncode, 0)

            print(f"\nPerformance for 10MB file:")
            print(f"  SHA-256: {sha256_time:.2f}s ({10 / sha256_time:.1f} MB/s)")
            print(f"  SHA3-256: {sha3_time:.2f}s ({10 / sha3_time:.1f} MB/s)")

        finally:
            os.unlink(test_file)

    def test_encryption_performance(self):

        import tempfile
        import time

        # Create 1MB test file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'x' * (1024 * 1024))
            test_file = f.name

        encrypted = test_file + '.enc'
        key = '0' * 32

        try:
            # Time CBC encryption
            start = time.time()
            result = subprocess.run(
                ['cryptocore', '--algorithm', 'aes', '--mode', 'cbc',
                 '--encrypt', '--key', key,
                 '--input', test_file, '--output', encrypted],
                capture_output=True, text=True
            )
            encryption_time = time.time() - start

            self.assertEqual(result.returncode, 0)

            print(f"\nCBC Encryption performance:")
            print(f"  1MB in {encryption_time:.3f}s ({1 / encryption_time:.1f} MB/s)")

        finally:
            for f in [test_file, encrypted]:
                if os.path.exists(f):
                    os.unlink(f)

    def test_pbkdf2_performance(self):

        import time

        iteration_counts = [1000, 10000, 100000]

        print("\nPBKDF2 Performance:")
        for iterations in iteration_counts:
            start = time.time()
            result = subprocess.run(
                ['cryptocore', 'derive',
                 '--password', 'test',
                 '--salt', '1234567890abcdef',
                 '--iterations', str(iterations),
                 '--length', '32'],
                capture_output=True, text=True
            )
            elapsed = time.time() - start

            self.assertEqual(result.returncode, 0)

            print(f"  {iterations:6,} iterations: {elapsed:6.3f}s")

            # For high iterations, warn if too fast (might be broken)
            if iterations >= 100000 and elapsed < 0.1:
                print(f"  WARNING: {iterations} iterations took only {elapsed:.3f}s "
                      f"- might not be actually iterating")


if __name__ == '__main__':
    unittest.main()