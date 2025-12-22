import unittest
import tempfile
import os
import sys
import subprocess
from src.cryptocore.csprng import (
    generate_random_bytes,
    generate_aes_key,
    generate_iv,
    is_key_weak
)


class TestCSPRNG(unittest.TestCase):
    def test_generate_random_bytes_basic(self):

        # Test different sizes
        for size in [1, 16, 32, 64, 128, 256]:
            data = generate_random_bytes(size)
            self.assertEqual(len(data), size)

    def test_generate_random_bytes_invalid_size(self):
        """Test error handling for invalid sizes."""
        with self.assertRaises(ValueError):
            generate_random_bytes(0)

        with self.assertRaises(ValueError):
            generate_random_bytes(-1)

    def test_generate_aes_key(self):
        """Test AES key generation."""
        key = generate_aes_key()
        self.assertEqual(len(key), 16)  # 128-bit key

        # Generate multiple keys and ensure they're different
        keys = set()
        for _ in range(10):
            key = generate_aes_key()
            keys.add(key.hex())

        self.assertEqual(len(keys), 10)  # All keys should be unique

    def test_generate_iv(self):

        iv = generate_iv()
        self.assertEqual(len(iv), 16)  # 16-byte IV

        # Generate multiple IVs and ensure they're different
        ivs = set()
        for _ in range(10):
            iv = generate_iv()
            ivs.add(iv.hex())

        self.assertEqual(len(ivs), 10)  # All IVs should be unique

    def test_is_key_weak(self):
        """Test weak key detection."""
        # Strong keys should return False
        strong_keys = [
            bytes([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]),
            bytes([i % 256 for i in range(16)]),  # Not simple sequential
        ]

        for key in strong_keys:
            self.assertFalse(is_key_weak(key), f"Key {key.hex()} should not be weak")

        # Weak keys should return True
        weak_keys = [
            bytes([0] * 16),  # All zeros
            bytes([0xFF] * 16),  # All ones
            bytes([i for i in range(16)]),  # Simple increasing sequence
            bytes([0xAA] * 16),  # Repeated byte
            bytes([0xAB, 0xCD] * 8),  # Repeated pattern
        ]

        for key in weak_keys:
            self.assertTrue(is_key_weak(key), f"Key {key.hex()} should be weak")

    def test_key_uniqueness_large_scale(self):

        num_keys = 1000
        keys_set = set()

        for i in range(num_keys):
            key = generate_aes_key()
            key_hex = key.hex()

            # Check for duplicates
            self.assertNotIn(key_hex, keys_set,
                             f"Duplicate key found at iteration {i}: {key_hex}")
            keys_set.add(key_hex)

        print(f"✓ Generated {len(keys_set)} unique AES keys")

    def test_randomness_statistics(self):

        # Generate a larger sample
        sample_size = 10000  # bytes
        data = generate_random_bytes(sample_size)

        # Count '1' bits
        ones_count = sum(bin(b).count('1') for b in data)
        total_bits = sample_size * 8

        # For random data, we expect about 50% ones
        ones_percentage = (ones_count / total_bits) * 100

        # Check it's close to 50% (allow some deviation)
        self.assertGreater(ones_percentage, 40,
                           f"Too few '1' bits: {ones_percentage:.1f}%")
        self.assertLess(ones_percentage, 60,
                        f"Too many '1' bits: {ones_percentage:.1f}%")

        print(f"✓ Randomness check: {ones_percentage:.1f}% bits set to 1 (expected ~50%)")

    def test_nist_preparation(self):

        # Skip in normal test runs as it generates large files
        if not os.getenv('RUN_NIST_PREP'):
            self.skipTest("NIST preparation test skipped (set RUN_NIST_PREP=1 to run)")

        total_size = 10_000_000  # 10 MB
        output_file = 'nist_test_data.bin'

        with open(output_file, 'wb') as f:
            bytes_written = 0
            chunk_size = 4096

            while bytes_written < total_size:
                chunk = generate_random_bytes(min(chunk_size, total_size - bytes_written))
                f.write(chunk)
                bytes_written += len(chunk)

        print(f"✓ Generated {bytes_written} bytes for NIST testing in '{output_file}'")

        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)

    def test_cli_key_generation(self):

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Test file for key generation"
            f.write(test_content)
            test_file = f.name

        encrypted_file = test_file + '.enc'
        decrypted_file = test_file + '.dec'

        try:
            # Run encryption without key (should generate one)
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore",
                    "--algorithm", "aes",
                    "--mode", "cbc",
                    "--encrypt",
                    "--input", test_file,
                    "--output", encrypted_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # Check that encryption succeeded and key was printed
            self.assertEqual(result.returncode, 0,
                             f"Encryption failed: {result.stderr}")

            self.assertIn("Generated key:", result.stdout)
            self.assertIn("[INFO]", result.stdout)

            # Extract the generated key from output
            import re
            key_match = re.search(r'Generated key: ([0-9a-f]{32})', result.stdout)
            self.assertIsNotNone(key_match, "Could not find generated key in output")

            generated_key = key_match.group(1)

            # Now decrypt with the generated key
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore",
                    "--algorithm", "aes",
                    "--mode", "cbc",
                    "--decrypt",
                    "--key", generated_key,
                    "--input", encrypted_file,
                    "--output", decrypted_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0,
                             f"Decryption failed: {result.stderr}")

            # Verify the decrypted file matches the original
            with open(test_file, 'rb') as f:
                original = f.read()

            with open(decrypted_file, 'rb') as f:
                decrypted = f.read()

            self.assertEqual(original, decrypted)

            print(f"✓ CLI key generation test passed")
            print(f"  Generated key: {generated_key}")

        finally:
            # Cleanup
            for file_path in [test_file, encrypted_file, decrypted_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)


if __name__ == '__main__':
    unittest.main()