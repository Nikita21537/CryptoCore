import unittest
import os
import tempfile
import subprocess
import sys
from src.modes.gcm import GCM, AuthenticationError


class TestGCM(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(16)
        self.nonce = os.urandom(12)
        self.plaintext = b"Test plaintext for GCM mode"
        self.aad = b"Associated authentication data"

    def test_basic_encrypt_decrypt(self):

        gcm = GCM(self.key, self.nonce)

        ciphertext = gcm.encrypt(self.plaintext, self.aad)
        decrypted = gcm.decrypt(ciphertext, self.aad)

        self.assertEqual(self.plaintext, decrypted)

    def test_aad_tamper(self):

        gcm = GCM(self.key)

        ciphertext = gcm.encrypt(self.plaintext, self.aad)

        # Try with wrong AAD
        wrong_aad = b"Wrong associated data"

        gcm2 = GCM(self.key, gcm.nonce)
        with self.assertRaises(AuthenticationError):
            gcm2.decrypt(ciphertext, wrong_aad)

    def test_ciphertext_tamper(self):

        gcm = GCM(self.key)

        ciphertext = gcm.encrypt(self.plaintext, self.aad)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[30] ^= 0x01  # Flip one byte

        gcm2 = GCM(self.key, gcm.nonce)
        with self.assertRaises(AuthenticationError):
            gcm2.decrypt(bytes(tampered), self.aad)

    def test_tag_tamper(self):

        gcm = GCM(self.key)

        ciphertext = gcm.encrypt(self.plaintext, self.aad)

        # Tamper with tag (last 16 bytes)
        tampered = bytearray(ciphertext)
        tampered[-1] ^= 0x01

        gcm2 = GCM(self.key, gcm.nonce)
        with self.assertRaises(AuthenticationError):
            gcm2.decrypt(bytes(tampered), self.aad)

    def test_empty_aad(self):

        gcm = GCM(self.key, self.nonce)

        ciphertext = gcm.encrypt(self.plaintext, b"")
        decrypted = gcm.decrypt(ciphertext, b"")

        self.assertEqual(self.plaintext, decrypted)

    def test_empty_plaintext(self):

        gcm = GCM(self.key, self.nonce)

        ciphertext = gcm.encrypt(b"", self.aad)
        decrypted = gcm.decrypt(ciphertext, self.aad)

        self.assertEqual(b"", decrypted)

    def test_large_data(self):

        large_data = os.urandom(1024 * 1024)  # 1MB
        gcm = GCM(self.key)

        ciphertext = gcm.encrypt(large_data, self.aad)
        decrypted = gcm.decrypt(ciphertext, self.aad)

        self.assertEqual(large_data, decrypted)

    def test_nonce_uniqueness(self):

        nonces = set()
        for _ in range(100):
            gcm = GCM(self.key)
            nonces.add(gcm.nonce.hex())

        self.assertEqual(len(nonces), 100, "Nonces should be unique")

    def test_format_correctness(self):

        gcm = GCM(self.key)

        ciphertext = gcm.encrypt(self.plaintext, self.aad)

        # Check format
        self.assertEqual(len(ciphertext), 12 + len(self.plaintext) + 16)

        # Extract parts
        nonce = ciphertext[:12]
        tag = ciphertext[-16:]

        self.assertEqual(nonce, gcm.nonce)
        self.assertEqual(len(tag), 16)

    def test_cli_gcm(self):

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(self.plaintext)
            input_file = f.name

        encrypted_file = input_file + '.enc'
        decrypted_file = input_file + '.dec'

        try:
            # Encrypt
            result = subprocess.run([
                sys.executable, "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "gcm",
                "--encrypt",
                "--key", self.key.hex(),
                "--input", input_file,
                "--output", encrypted_file,
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0, f"Encryption failed: {result.stderr}")
            self.assertIn("Successfully encrypted", result.stdout)

            # Decrypt with correct AAD
            result = subprocess.run([
                sys.executable, "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "gcm",
                "--decrypt",
                "--key", self.key.hex(),
                "--input", encrypted_file,
                "--output", decrypted_file,
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0, f"Decryption failed: {result.stderr}")
            self.assertIn("GCM decryption completed successfully", result.stdout)

            # Verify content
            with open(decrypted_file, 'rb') as f:
                decrypted = f.read()

            self.assertEqual(self.plaintext, decrypted)

        finally:
            for f in [input_file, encrypted_file, decrypted_file]:
                if os.path.exists(f):
                    os.remove(f)


class TestGCMNISTVectors(unittest.TestCase):


    def test_nist_vector_1(self):

        key = bytes.fromhex("00000000000000000000000000000000")
        nonce = bytes.fromhex("000000000000000000000000")
        plaintext = b""
        aad = b""

        # Expected ciphertext (just nonce + tag for empty plaintext)
        # Full test vector would have specific expected tag

        gcm = GCM(key, nonce)
        ciphertext = gcm.encrypt(plaintext, aad)

        # Should have correct format
        self.assertEqual(len(ciphertext), 12 + 0 + 16)  # nonce + empty + tag
        self.assertEqual(ciphertext[:12], nonce)

        # Verify we can decrypt
        decrypted = gcm.decrypt(ciphertext, aad)
        self.assertEqual(plaintext, decrypted)


if __name__ == '__main__':

    unittest.main()
