import unittest
import tempfile
import os
import subprocess
import sys
from src.mac import HMAC, HMACStream, AESCMAC


class TestHMAC(unittest.TestCase):


    def test_rfc_4231_test_case_1(self):

        key = bytes([0x0b] * 20)  # 20 bytes of 0x0b
        message = b"Hi There"

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)
        expected = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"

        self.assertEqual(result, expected, "RFC 4231 Test Case 1 failed")

    def test_rfc_4231_test_case_2(self):

        key = b"Jefe"
        message = b"what do ya want for nothing?"

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)
        expected = "5bdcc146bf05454e6a042426089575c75a003f089d2739839dec58b964ec3843"

        self.assertEqual(result, expected, "RFC 4231 Test Case 2 failed")

    def test_key_shorter_than_block(self):

        key = b"short_key"
        message = b"Test message"

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)

        # Just verify it produces a valid hash
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    def test_key_longer_than_block(self):

        key = b"A" * 100  # 100 bytes > 64 byte block size
        message = b"Test message"

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)

        # Verify it produces a valid hash
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    def test_key_exactly_block_size(self):

        key = b"B" * 64  # Exactly 64 bytes
        message = b"Test message"

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)

        # Verify it produces a valid hash
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    def test_empty_message(self):

        key = b"test_key"
        message = b""

        hmac = HMAC(key, 'sha256')
        result = hmac.compute_hex(message)

        # Should produce valid HMAC for empty message
        self.assertEqual(len(result), 64)

    def test_verification(self):

        key = b"secret_key"
        message = b"Important data"

        hmac = HMAC(key, 'sha256')
        mac_value = hmac.compute(message)

        # Should verify correctly
        self.assertTrue(hmac.verify(message, mac_value))

        # Should fail with wrong message
        self.assertFalse(hmac.verify(b"Tampered data", mac_value))

        # Should fail with wrong key
        wrong_hmac = HMAC(b"wrong_key", 'sha256')
        self.assertFalse(wrong_hmac.verify(message, mac_value))

    def test_streaming_hmac(self):

        key = b"streaming_key"
        message = b"Large message " * 1000  # ~14KB

        # Compute with one-shot
        hmac_one_shot = HMAC(key, 'sha256')
        result_one_shot = hmac_one_shot.compute_hex(message)

        # Compute with streaming
        hmac_stream = HMACStream(key, 'sha256')

        # Process in chunks
        chunk_size = 1024
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i + chunk_size]
            hmac_stream.update(chunk)

        result_streaming = hmac_stream.finalize_hex()

        # Results should match
        self.assertEqual(result_one_shot, result_streaming, "Streaming HMAC mismatch")

    def test_tamper_detection(self):

        key = b"secure_key"
        original_message = b"Original content"
        tampered_message = b"Tampered content"

        hmac = HMAC(key, 'sha256')
        mac_original = hmac.compute(original_message)

        # Verify original (should succeed)
        self.assertTrue(hmac.verify(original_message, mac_original))

        # Verify tampered (should fail)
        self.assertFalse(hmac.verify(tampered_message, mac_original))

    def test_different_keys_produce_different_hmac(self):

        message = b"Same message"

        hmac1 = HMAC(b"key1", 'sha256')
        hmac2 = HMAC(b"key2", 'sha256')

        result1 = hmac1.compute_hex(message)
        result2 = hmac2.compute_hex(message)

        self.assertNotEqual(result1, result2, "Different keys should produce different HMACs")


class TestAESCMAC(unittest.TestCase):


    def test_cmac_basic(self):

        key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")  # AES-128 key
        message = b""

        cmac = AESCMAC(key)
        result = cmac.compute_hex(message)

        # Just verify it produces output
        self.assertEqual(len(result), 32)  # 16 bytes = 32 hex chars

    def test_cmac_nist_test_vector(self):

        # Example test vector (simplified)
        key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
        message = bytes.fromhex("6bc1bee22e409f96e93d7e117393172a")

        cmac = AESCMAC(key)
        result = cmac.compute_hex(message)

        # This is a simplified test - in real implementation would use NIST vectors
        self.assertEqual(len(result), 32)

    def test_cmac_verification(self):

        key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
        message = b"Test message for CMAC"

        cmac = AESCMAC(key)
        mac_value = cmac.compute(message)

        # Should verify correctly
        self.assertTrue(cmac.verify(message, mac_value))

        # Should fail with wrong message
        self.assertFalse(cmac.verify(b"Wrong message", mac_value))

        # Should fail with wrong key
        wrong_cmac = AESCMAC(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
        self.assertFalse(wrong_cmac.verify(message, mac_value))


class TestCLIHMAC(unittest.TestCase):


    def test_cli_hmac_generation(self):

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Data to authenticate"
            f.write(test_content)
            test_file = f.name

        hmac_file = test_file + '.hmac'

        try:

            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",
                    "--input", test_file,
                    "--output", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0,
                             f"HMAC generation failed: {result.stderr}")

            # Read HMAC from file
            with open(hmac_file, 'r') as f:
                hmac_line = f.read().strip()


            hmac_value, filename = hmac_line.split()
            self.assertEqual(filename, test_file)


            self.assertEqual(len(hmac_value), 64)
            self.assertTrue(all(c in '0123456789abcdef' for c in hmac_value.lower()))

            print(f"✓ CLI HMAC generation test passed: {hmac_value[:16]}...")

        finally:
            # Cleanup
            for file_path in [test_file, hmac_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    def test_cli_hmac_verification(self):

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Data to authenticate and verify"
            f.write(test_content)
            test_file = f.name

        hmac_file = test_file + '.hmac'

        try:

            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",
                    "--input", test_file,
                    "--output", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0, "HMAC generation failed")

            # Now verify it
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",
                    "--input", test_file,
                    "--verify", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0,
                             f"HMAC verification failed: {result.stderr}")

            self.assertIn("[OK] HMAC verification successful", result.stdout)

            print(f"✓ CLI HMAC verification test passed")

        finally:

            for file_path in [test_file, hmac_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    def test_cli_hmac_tamper_detection(self):


        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            original_content = b"Original data"
            f.write(original_content)
            test_file = f.name

        hmac_file = test_file + '.hmac'

        try:
            # Generate HMAC for original content
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",
                    "--input", test_file,
                    "--output", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0, "HMAC generation failed")

            # Tamper with the file
            with open(test_file, 'wb') as f:
                f.write(b"Tampered data")

            # Try to verify - should fail
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",
                    "--input", test_file,
                    "--verify", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertNotEqual(result.returncode, 0,
                                "HMAC verification should have failed for tampered data")
            self.assertIn("[ERROR]", result.stderr)

            print(f"✓ CLI HMAC tamper detection test passed")

        finally:
            # Cleanup
            for file_path in [test_file, hmac_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    def test_cli_hmac_wrong_key_detection(self):

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            test_content = b"Data to authenticate"
            f.write(test_content)
            test_file = f.name

        hmac_file = test_file + '.hmac'

        try:
            # Generate HMAC with key1
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "00112233445566778899aabbccddeeff",  # key1
                    "--input", test_file,
                    "--output", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertEqual(result.returncode, 0, "HMAC generation failed")

            # Try to verify with different key - should fail
            result = subprocess.run(
                [
                    sys.executable, "-m", "src.cryptocore", "dgst",
                    "--algorithm", "sha256",
                    "--hmac",
                    "--key", "ffeeddccbbaa99887766554433221100",  # key2 (different)
                    "--input", test_file,
                    "--verify", hmac_file
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            self.assertNotEqual(result.returncode, 0,
                                "HMAC verification should have failed with wrong key")
            self.assertIn("[ERROR]", result.stderr)

            print(f"✓ CLI HMAC wrong key detection test passed")

        finally:
            # Cleanup
            for file_path in [test_file, hmac_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)


if __name__ == '__main__':
    unittest.main()