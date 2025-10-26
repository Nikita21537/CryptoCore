import unittest
import os
import tempfile
from src.modes.ecb import pkcs7_pad, pkcs7_unpad, encrypt_ecb, decrypt_ecb

class TestCryptoCore(unittest.TestCase):
    
    def test_pkcs7_pad(self):
        # Тест дополнения
        data = b"hello"
        padded = pkcs7_pad(data)
        self.assertEqual(len(padded) % 16, 0)
        self.assertEqual(padded[-1], 11)  # 16 - 5 = 11 байт дополнения
        
        # Тест с данными кратными 16 байтам
        data = b"a" * 16
        padded = pkcs7_pad(data)
        self.assertEqual(len(padded), 32)  # Должен добавить целый блок
        self.assertEqual(padded[-1], 16)
    
    def test_pkcs7_unpad(self):
        # Тест удаления дополнения
        original = b"hello"
        padded = pkcs7_pad(original)
        unpadded = pkcs7_unpad(padded)
        self.assertEqual(original, unpadded)
        
        # Тест с данными кратными 16 байтам
        original = b"a" * 16
        padded = pkcs7_pad(original)
        unpadded = pkcs7_unpad(padded)
        self.assertEqual(original, unpadded)
    
    def test_encrypt_decrypt_ecb(self):
        # Тест шифрования и дешифрования
        key = b'\x00' * 16  # Тестовый ключ
        plaintext = b"Hello, CryptoCore! This is a test message."
        
        # Шифрование
        ciphertext = encrypt_ecb(plaintext, key)
        self.assertNotEqual(plaintext, ciphertext)
        self.assertEqual(len(ciphertext) % 16, 0)
        
        # Дешифрование
        decrypted = decrypt_ecb(ciphertext, key)
        self.assertEqual(plaintext, decrypted)
    
    def test_empty_data(self):
        # Тест с пустыми данными
        key = b'\x00' * 16
        plaintext = b""
        
        ciphertext = encrypt_ecb(plaintext, key)
        decrypted = decrypt_ecb(ciphertext, key)
        self.assertEqual(plaintext, decrypted)

if __name__ == '__main__':
    unittest.main()
