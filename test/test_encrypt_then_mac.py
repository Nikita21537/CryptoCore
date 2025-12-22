import unittest
import os
import tempfile
import subprocess
import sys
from src.cryptocore.modes.encrypt_then_mac import EncryptThenMAC, AuthenticationError


class TestEncryptThenMAC(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32)  # 32 bytes for enc + mac
        self.plaintext = b"Test message for Encrypt-then-MAC"
        self.aad = b"Authentication data"

    def test_basic_operation(self):

        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(self.plaintext, self.aad)
        decrypted = etm.decrypt(ciphertext, self.aad)

        self.assertEqual(self.plaintext, decrypted)

    def test_different_modes(self):

        for mode in ['cbc', 'ctr', 'cfb']:
            with self.subTest(mode=mode):
                etm = EncryptThenMAC(mode, self.key)

                ciphertext = etm.encrypt(self.plaintext, self.aad)
                decrypted = etm.decrypt(ciphertext, self.aad)

                self.assertEqual(self.plaintext, decrypted)

    def test_aad_tamper(self):

        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(self.plaintext, self.aad)

        # Try with wrong AAD
        with self.assertRaises(AuthenticationError):
            etm.decrypt(ciphertext, b"wrong aad")

    def test_ciphertext_tamper(self):

        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(self.plaintext, self.aad)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[20] ^= 0x01

        with self.assertRaises(AuthenticationError):
            etm.decrypt(bytes(tampered), self.aad)

    def test_key_separation(self):

        key1 = os.urandom(32)
        key2 = os.urandom(32)

        etm1 = EncryptThenMAC('cbc', key1)
        etm2 = EncryptThenMAC('cbc', key2)

        ciphertext1 = etm1.encrypt(self.plaintext, self.aad)
        ciphertext2 = etm2.encrypt(self.plaintext, self.aad)

        # Should be different
        self.assertNotEqual(ciphertext1, ciphertext2)

        # Each should decrypt with its own key
        decrypted1 = etm1.decrypt(ciphertext1, self.aad)
        decrypted2 = etm2.decrypt(ciphertext2, self.aad)

        self.assertEqual(self.plaintext, decrypted1)
        self.assertEqual(self.plaintext, decrypted2)

        # Should fail with wrong key
        with self.assertRaises(AuthenticationError):
            etm1.decrypt(ciphertext2, self.aad)

    def test_empty_aad(self):

        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(self.plaintext, b"")
        decrypted = etm.decrypt(ciphertext, b"")

        self.assertEqual(self.plaintext, decrypted)

    def test_empty_plaintext(self):

        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(b"", self.aad)
        decrypted = etm.decrypt(ciphertext, self.aad)

        self.assertEqual(b"", decrypted)

    def test_large_data(self):

        large_data = os.urandom(1024 * 1024)  # 1MB
        etm = EncryptThenMAC('cbc', self.key)

        ciphertext = etm.encrypt(large_data, self.aad)
        decrypted = etm.decrypt(ciphertext, self.aad)

        self.assertEqual(large_data, decrypted)

    def test_cli_etm(self):

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
                "--mode", "etm",
                "--encrypt",
                "--key", self.key.hex(),
                "--input", input_file,
                "--output", encrypted_file,
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0, f"Encryption failed: {result.stderr}")

            # Decrypt with correct AAD
            result = subprocess.run([
                sys.executable, "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "etm",
                "--decrypt",
                "--key", self.key.hex(),
                "--input", encrypted_file,
                "--output", decrypted_file,
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0, f"Decryption failed: {result.stderr}")
            self.assertIn("Encrypt-then-MAC decryption completed successfully", result.stdout)

            # Verify content
            with open(decrypted_file, 'rb') as f:
                decrypted = f.read()

            self.assertEqual(self.plaintext, decrypted)

        finally:
            for f in [input_file, encrypted_file, decrypted_file]:
                if os.path.exists(f):
                    os.remove(f)

    def test_cli_etm_tamper(self):

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(self.plaintext)
            input_file = f.name

        encrypted_file = input_file + '.enc'

        try:
            # Encrypt
            subprocess.run([
                sys.executable, "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "etm",
                "--encrypt",
                "--key", self.key.hex(),
                "--input", input_file,
                "--output", encrypted_file,
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            # Tamper with encrypted file
            with open(encrypted_file, 'rb') as f:
                data = bytearray(f.read())

            data[50] ^= 0x01  # Flip one byte

            with open(encrypted_file, 'wb') as f:
                f.write(data)

            # Try to decrypt - should fail
            result = subprocess.run([
                sys.executable, "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "etm",
                "--decrypt",
                "--key", self.key.hex(),
                "--input", encrypted_file,
                "--output", "/dev/null",  # Shouldn't create this
                "--aad", self.aad.hex()
            ], capture_output=True, text=True)

            self.assertNotEqual(result.returncode, 0, "Should have failed")
            self.assertIn("authentication failed", result.stderr.lower())

        finally:
            for f in [input_file, encrypted_file]:
                if os.path.exists(f):
                    os.remove(f)


if __name__ == '__main__':
    unittest.main()