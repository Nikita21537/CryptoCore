from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from src.modes.ecb import ECBCipher
from src.modes.cbc import CBCCipher
from src.modes.cfb import CFBCipher
from src.modes.ofb import OFBCipher
from src.modes.ctr import CTRCipher

class CryptoCore:
    def __init__(self, algorithm, mode, key):
        if algorithm != 'aes':
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        self.algorithm = algorithm
        self.mode = mode
        self.key = key
        self.block_size = 16
        
        # Создаем базовый cipher AES
        self.aes_cipher = AES.new(key, AES.MODE_ECB)
        
        # Выбираем режим
        self.mode_handler = self._get_mode_handler(mode)
    
    def _get_mode_handler(self, mode):
        handlers = {
            'ecb': ECBCipher,
            'cbc': CBCCipher,
            'cfb': CFBCipher,
            'ofb': OFBCipher,
            'ctr': CTRCipher
        }
        
        if mode not in handlers:
            raise ValueError(f"Unsupported mode: {mode}")
            
        return handlers[mode](self.aes_cipher, self.block_size)
    
    def encrypt(self, plaintext):
        return self.mode_handler.encrypt(plaintext)
    
    def decrypt(self, ciphertext, iv=None):
        if iv and self.mode in ['cbc', 'cfb', 'ofb', 'ctr']:
            # Если IV предоставлен извне, используем его
            ciphertext = iv + ciphertext
        
        return self.mode_handler.decrypt(ciphertext)
        
