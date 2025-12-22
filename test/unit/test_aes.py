import unittest
import os
import sys
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.cryptocore.modes.ecb import AES_ECB, PKCS7Padding
from src.cryptocore.modes.cbc import AES_CBC
from src.cryptocore.modes.cfb import AES_CFB
from src.cryptocore.modes import AES_OFB
from src.cryptocore.modes.ctr import AES_CTR


class TestPKCS7Padding(unittest.TestCase):


    def test_pad_unpad_roundtrip(self):

        test_cases = [
            b"",
            b"A",
            b"AB",
            b"ABC",
            b"ABCD",
            b"ABCDE",
            b"ABCDEF",
            b"ABCDEFG",
            b"ABCDEFGH",
            b"ABCDEFGHI",
            b"ABCDEFGHIJ",
            b"ABCDEFGHIJK",
            b"ABCDEFGHIJKL",
            b"ABCDEFGHIJKLM",
            b"ABCDEFGHIJKLMN",
            b"ABCDEFGHIJKLMNO",
            b"ABCDEFGHIJKLMNOP",  # Exactly one block
        ]

        for data in test_cases:
            with self.subTest(data=data):
                padded = PKCS7Padding.pad(data, 16)
                unpadded = PKCS7Padding.unpad(padded)
                self.assertEqual(data, unpadded, f"Failed for data: {data}")

    def test_pad_length(self):

        test_cases = [
            (b"", 16),
            (b"A", 15),
            (b"AB", 14),
            (b"ABC", 13),
            (b"A" * 15, 1),
            (b"A" * 16, 16),  # Full block of padding
        ]

        for data, expected_padding in test_cases:
            with self.subTest(data=data):
                padded = PKCS7Padding.pad(data, 16)
                self.assertEqual(len(padded) % 16, 0)
                self.assertEqual(padded[-1], expected_padding)

    def test_unpad_invalid(self):

        # Valid padding
        padded = PKCS7Padding.pad(b"test", 16)
        unpadded = PKCS7Padding.unpad(padded)
        self.assertEqual(unpadded, b"test")

        # Invalid: padding value too large
        invalid = b"test" + b"\x11" * 17  # 0x11 = 17 > block size
        with self.assertRaises(ValueError):
            PKCS7Padding.unpad(invalid)

        # Invalid: inconsistent padding
        invalid = b"test" + b"\x04\x04\x03\x04"
        with self.assertRaises(ValueError):
            PKCS7Padding.unpad(invalid)

        # Invalid: zero padding
        invalid = b"test" + b"\x00" * 4
        with self.assertRaises(ValueError):
            PKCS7Padding.unpad(invalid)


class TestAESECB(unittest.TestCase):


    def setUp(self):
        self.key = b"0123456789abcdef"
        self.aes = AES_ECB(self.key)

    def test_encrypt_decrypt_roundtrip(self):

        test_cases = [
            b"",
            b"A",
            b"Hello, World!",
            b"This is a longer test message for encryption.",
            b"A" * 100,  # Multiple blocks
            b"B" * 15,  # Edge case: less than block
            b"C" * 16,  # Exactly one block
            b"D" * 17,  # Just over one block
        ]

        for plaintext in test_cases:
            with self.subTest(plaintext=plaintext):
                ciphertext = self.aes.encrypt(plaintext)
                decrypted = self.aes.decrypt(ciphertext)
                self.assertEqual(plaintext, decrypted)

    def test_deterministic(self):

        plaintext = b"Test message"
        ciphertext1 = self.aes.encrypt(plaintext)
        ciphertext2 = self.aes.encrypt(plaintext)
        self.assertEqual(ciphertext1, ciphertext2)

    def test_different_keys(self):

        plaintext = b"Same plaintext"

        key1 = b"0123456789abcdef"
        key2 = b"fedcba9876543210"

        aes1 = AES_ECB(key1)
        aes2 = AES_ECB(key2)

        ciphertext1 = aes1.encrypt(plaintext)
        ciphertext2 = aes2.encrypt(plaintext)

        self.assertNotEqual(ciphertext1, ciphertext2)

    def test_block_size_requirement(self):

        plaintexts = [b"A", b"AB", b"ABC", b"ABCD", b"A" * 17]

        for plaintext in plaintexts:
            ciphertext = self.aes.encrypt(plaintext)
            self.assertEqual(len(ciphertext) % 16, 0)


class TestAESCBC(unittest.TestCase):


    def setUp(self):
        self.key = b"0123456789abcdef"
        self.iv = b"1234567890abcdef"

    def test_encrypt_decrypt_roundtrip(self):

        cbc = AES_CBC(self.key, self.iv)

        test_cases = [
            b"",
            b"Hello, CBC!",
            b"This is a test message for CBC mode encryption.",
            b"A" * 100,
            b"B" * 15,
            b"C" * 16,
            b"D" * 17,
        ]

        for plaintext in test_cases:
            with self.subTest(plaintext=plaintext):
                ciphertext = cbc.encrypt(plaintext)
                decrypted = cbc.decrypt(ciphertext)
                self.assertEqual(plaintext, decrypted)

    def test_iv_effect(self):

        plaintext = b"Same plaintext"

        iv1 = b"1111111111111111"
        iv2 = b"2222222222222222"

        cbc1 = AES_CBC(self.key, iv1)
        cbc2 = AES_CBC(self.key, iv2)

        ciphertext1 = cbc1.encrypt(plaintext)
        ciphertext2 = cbc2.encrypt(plaintext)

        self.assertNotEqual(ciphertext1, ciphertext2)

    def test_ciphertext_tamper(self):

        cbc = AES_CBC(self.key, self.iv)
        plaintext = b"Original message"

        ciphertext = cbc.encrypt(plaintext)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[10] ^= 0x01  # Flip one byte

        decrypted = cbc.decrypt(bytes(tampered))

        # In CBC, one flipped byte affects two blocks
        self.assertNotEqual(plaintext, decrypted)


class TestStreamModes(unittest.TestCase):


    def setUp(self):
        self.key = b"0123456789abcdef"
        self.iv = b"1234567890abcdef"

    def test_cfb_mode(self):

        cfb = AES_CFB(self.key, self.iv)

        test_cases = [
            b"",
            b"A",
            b"Hello, CFB!",
            b"This is CFB mode test",
            b"X" * 100,
        ]

        for plaintext in test_cases:
            with self.subTest(plaintext=plaintext, mode="CFB"):
                ciphertext = cfb.encrypt(plaintext)
                self.assertEqual(len(ciphertext), len(plaintext))

                decrypted = cfb.decrypt(ciphertext)
                self.assertEqual(plaintext, decrypted)

    def test_ofb_mode(self):

        ofb = AES_OFB(self.key, self.iv)

        test_cases = [
            b"",
            b"B",
            b"Hello, OFB!",
            b"This is OFB mode test",
            b"Y" * 100,
        ]

        for plaintext in test_cases:
            with self.subTest(plaintext=plaintext, mode="OFB"):
                ciphertext = ofb.encrypt(plaintext)
                self.assertEqual(len(ciphertext), len(plaintext))

                decrypted = ofb.decrypt(ciphertext)
                self.assertEqual(plaintext, decrypted)

    def test_ctr_mode(self):

        ctr = AES_CTR(self.key, self.iv)

        test_cases = [
            b"",
            b"C",
            b"Hello, CTR!",
            b"This is CTR mode test",
            b"Z" * 100,
        ]

        for plaintext in test_cases:
            with self.subTest(plaintext=plaintext, mode="CTR"):
                ciphertext = ctr.encrypt(plaintext)
                self.assertEqual(len(ciphertext), len(plaintext))

                decrypted = ctr.decrypt(ciphertext)
                self.assertEqual(plaintext, decrypted)

    def test_stream_parallel_encryption(self):

        plaintext = b"Test message for parallel operations"

        # Encrypt first half
        cfb1 = AES_CFB(self.key, self.iv)
        ciphertext1 = cfb1.encrypt(plaintext[:10])

        # Encrypt second half with same state
        ciphertext2 = cfb1.encrypt(plaintext[10:])

        # Decrypt with fresh instance
        cfb2 = AES_CFB(self.key, self.iv)
        decrypted1 = cfb2.decrypt(ciphertext1)
        decrypted2 = cfb2.decrypt(ciphertext2)

        self.assertEqual(decrypted1 + decrypted2, plaintext)


class TestNISTVectors(unittest.TestCase):


    def load_nist_vectors(self, filename):
        """Load NIST test vectors from JSON file."""
        vectors_path = os.path.join(
            os.path.dirname(__file__), '../vectors', filename
        )

        if not os.path.exists(vectors_path):
            self.skipTest(f"Test vectors not found: {filename}")

        with open(vectors_path, 'r') as f:
            return json.load(f)

    def test_ecb_nist_vectors(self):

        vectors = self.load_nist_vectors('nist_aes.json')
        ecb_vectors = vectors.get('ECB', [])

        for i, vector in enumerate(ecb_vectors):
            with self.subTest(vector=i):
                key = bytes.fromhex(vector['key'])
                plaintext = bytes.fromhex(vector['plaintext'])
                expected = bytes.fromhex(vector['ciphertext'])

                aes = AES_ECB(key)
                ciphertext = aes.encrypt(plaintext)

                self.assertEqual(ciphertext, expected)

                # Also test decryption
                decrypted = aes.decrypt(ciphertext)
                self.assertEqual(decrypted, plaintext)

        print(f"✓ Passed {len(ecb_vectors)} NIST ECB test vectors")

    def test_cbc_nist_vectors(self):

        vectors = self.load_nist_vectors('nist_aes.json')
        cbc_vectors = vectors.get('CBC', [])

        for i, vector in enumerate(cbc_vectors):
            with self.subTest(vector=i):
                key = bytes.fromhex(vector['key'])
                iv = bytes.fromhex(vector['iv'])
                plaintext = bytes.fromhex(vector['plaintext'])
                expected = bytes.fromhex(vector['ciphertext'])

                cbc = AES_CBC(key, iv)
                ciphertext = cbc.encrypt(plaintext)

                self.assertEqual(ciphertext, expected)

                # Also test decryption
                decrypted = cbc.decrypt(ciphertext)
                self.assertEqual(decrypted, plaintext)

        print(f"✓ Passed {len(cbc_vectors)} NIST CBC test vectors")


class TestErrorHandling(unittest.TestCase):


    def test_invalid_key_length(self):

        # Too short
        with self.assertRaises(ValueError):
            AES_ECB(b"short")

        # Too long
        with self.assertRaises(ValueError):
            AES_ECB(b"toolongkey" * 3)

        # Valid
        try:
            AES_ECB(b"0123456789abcdef")
        except ValueError:
            self.fail("Valid key should not raise ValueError")

    def test_invalid_iv_length(self):

        key = b"0123456789abcdef"

        # Too short
        with self.assertRaises(ValueError):
            AES_CBC(key, b"shortiv")

        # Too long
        with self.assertRaises(ValueError):
            AES_CBC(key, b"toolongiv" * 3)

        # Valid
        try:
            AES_CBC(key, b"0123456789abcdef")
        except ValueError:
            self.fail("Valid IV should not raise ValueError")

    def test_invalid_ciphertext_length(self):

        key = b"0123456789abcdef"
        aes = AES_ECB(key)

        # Not multiple of block size
        with self.assertRaises(ValueError):
            aes.decrypt(b"notmultipleof16")


        result = aes.decrypt(b"")
        self.assertEqual(result, b"")


        ciphertext = aes.encrypt(b"test")
        try:
            aes.decrypt(ciphertext)
        except ValueError:
            self.fail("Valid ciphertext should not raise ValueError")


if __name__ == '__main__':
    unittest.main()