import unittest
import os
import tempfile
from src.modes.ecb import AES_ECB, PKCS7Padding
import subprocess


class TestPKCS7Padding(unittest.TestCase):
    def test_pad_unpad(self):
        test_data = b"Hello World!"
        padded = PKCS7Padding.pad(test_data, 16)
        unpadded = PKCS7Padding.unpad(padded)
        self.assertEqual(test_data, unpadded)

    def test_exact_block_size(self):
        test_data = b"A" * 16
        padded = PKCS7Padding.pad(test_data, 16)
        self.assertEqual(len(padded), 32)  # Should add full block of padding
        unpadded = PKCS7Padding.unpad(padded)
        self.assertEqual(test_data, unpadded)


class TestAESECB(unittest.TestCase):
    def setUp(self):
        self.key = b"0123456789abcdef"
        self.aes = AES_ECB(self.key)

    def test_encrypt_decrypt(self):
        plaintext = b"Test message for encryption"
        ciphertext = self.aes.encrypt(plaintext)
        decrypted = self.aes.decrypt(ciphertext)
        self.assertEqual(plaintext, decrypted)

    def test_empty_data(self):
        plaintext = b""
        ciphertext = self.aes.encrypt(plaintext)
        decrypted = self.aes.decrypt(ciphertext)
        self.assertEqual(plaintext, decrypted)


class TestCLI(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            original_content = b"This is a test file content for encryption."
            f.write(original_content)
            original_file = f.name

        encrypted_file = original_file + ".enc"
        decrypted_file = original_file + ".dec"

        try:
            # Encrypt
            subprocess.run([
                "python", "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "ecb",
                "--encrypt",
                "--key", "000102030405060708090a0b0c0d0e0f",
                "--input", original_file,
                "--output", encrypted_file
            ], check=True)

            # Decrypt
            subprocess.run([
                "python", "-m", "src.cryptocore",
                "--algorithm", "aes",
                "--mode", "ecb",
                "--decrypt",
                "--key", "000102030405060708090a0b0c0d0e0f",
                "--input", encrypted_file,
                "--output", decrypted_file
            ], check=True)

            # Verify
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()

            self.assertEqual(original_content, decrypted_content)

        finally:
            # Cleanup
            for f in [original_file, encrypted_file, decrypted_file]:
                if os.path.exists(f):
                    os.remove(f)


if __name__ == '__main__':

    unittest.main()
