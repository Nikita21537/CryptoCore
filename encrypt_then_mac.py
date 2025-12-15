
import os
import hashlib
from typing import Union
from src.ciphers.aes import AES
from src.modes import get_mode
from src.mac.hmac import HMAC

class EncryptThenMAC:
    def __init__(self, 
                 enc_key: bytes, 
                 mac_key: bytes = None, 
                 mode: str = 'ctr',
                 mac_algorithm: str = 'sha256'):
       
        self.encryptor = get_mode(mode, enc_key)
        self.mac_algorithm = mac_algorithm
        
        if mac_key is None:
            # Derive MAC key from encryption key using HKDF-like approach
            h = hashlib.sha256(b"MAC_KEY_DERIVATION" + enc_key).digest()
            mac_key = h[:len(enc_key)]
            
        self.hmac = HMAC(mac_key, algorithm=mac_algorithm)
    
    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
       
        ciphertext = self.encryptor.encrypt(plaintext)
        
        tag = self.hmac.compute(ciphertext + aad)
        
        return ciphertext + tag
    
    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:
       
        if self.mac_algorithm == 'sha256':
            tag_len = 32
        elif self.mac_algorithm == 'sha1':
            tag_len = 20
        else:
            tag_len = 16  # Default
        
        if len(data) < tag_len:
            raise ValueError("Data too short")
        
        
        ciphertext = data[:-tag_len]
        tag = data[-tag_len:]
        
        computed_tag = self.hmac.compute(ciphertext + aad)
        
        if not self._constant_time_compare(tag, computed_tag):
            raise ValueError("Authentication failed: MAC mismatch")
        
        
        plaintext = self.encryptor.decrypt(ciphertext)
        
        return plaintext
    
    def _constant_time_compare(self, a: bytes, b: bytes) -> bool:
     
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        return result == 0
