import unittest
import os
import tempfile
from src.mac.hmac import HMAC

class TestHMAC(unittest.TestCase):
    def test_rfc_4231_test_case_1(self):
        
        key = bytes([0x0b] * 20)  # 20 байт 0x0b
        data = b"Hi There"
        expected = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        
        hmac = HMAC(key)
        result = hmac.compute(data)
        self.assertEqual(result, expected)
    
    def test_rfc_4231_test_case_2(self):
     
        key = b"Jefe"
        data = b"what do ya want for nothing?"
        expected = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        
        hmac = HMAC(key)
        result = hmac.compute(data)
        self.assertEqual(result, expected)
    
    def test_key_shorter_than_block(self):
        
        key = b"short_key"
        data = b"test message"
        
        hmac = HMAC(key)
        result1 = hmac.compute(data)
        
        # Должен работать одинаково с тем же ключом
        hmac2 = HMAC(key)
        result2 = hmac2.compute(data)
        
        self.assertEqual(result1, result2)
    
    def test_key_longer_than_block(self):
       
        key = b"x" * 100  # 100 байт
        data = b"test message"
        
        hmac = HMAC(key)
        result = hmac.compute(data)
        # Проверяем, что результат имеет правильную длину
        self.assertEqual(len(result), 64)  # 64 hex символа = 32 байта
    
    def test_empty_message(self):
        
        key = b"test_key"
        data = b""
        
        hmac = HMAC(key)
        result = hmac.compute(data)
        # Проверяем, что результат имеет правильную длину
        self.assertEqual(len(result), 64)
    
    def test_file_hmac(self):
       
        key = b"test_key"
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"test content")
            temp_file = f.name
        
        try:
            hmac = HMAC(key)
            result = hmac.compute_file(temp_file)
            self.assertEqual(len(result), 64)
        finally:
            os.unlink(temp_file)
    
    def test_hex_key(self):
       
        hex_key = "00112233445566778899aabbccddeeff"
        data = b"test message"
        
        hmac = HMAC(hex_key)
        result1 = hmac.compute(data)
        
        # Тот же ключ в байтах
        hmac2 = HMAC(bytes.fromhex(hex_key))
        result2 = hmac2.compute(data)
        
        self.assertEqual(result1, result2)
    
    def test_tamper_detection(self):
      
        key = b"secret_key"
        original_data = b"original message"
        modified_data = b"modified message"
        
        hmac = HMAC(key)
        original_hmac = hmac.compute(original_data)
        modified_hmac = hmac.compute(modified_data)
        
        self.assertNotEqual(original_hmac, modified_hmac)
    
    def test_key_sensitivity(self):
       
        data = b"test message"
        key1 = b"key1"
        key2 = b"key2"
        
        hmac1 = HMAC(key1)
        hmac2 = HMAC(key2)
        
        result1 = hmac1.compute(data)
        result2 = hmac2.compute(data)
        
        self.assertNotEqual(result1, result2)

if __name__ == '__main__':
    unittest.main()
