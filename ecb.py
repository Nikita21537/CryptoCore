from Crypto.Util.Padding import pad, unpad
from src.modes.mode_interface import ModeInterface

class ECBCipher(ModeInterface):
    def __init__(self, cipher, block_size=16, rng_function=None):
        self.cipher = cipher
        self.block_size = block_size
        # ECB не использует IV, поэтому rng_function не нужен

    def encrypt(self, plaintext):
        # Добавляем padding
        plaintext = pad(plaintext, self.block_size)
        
        # Разбиваем на блоки и шифруем каждый
        blocks = [plaintext[i:i+self.block_size] for i in range(0, len(plaintext), self.block_size)]
        ciphertext = b''.join([self.cipher.encrypt(block) for block in blocks])
        
        return ciphertext

    def decrypt(self, ciphertext):
        # Разбиваем на блоки и дешифруем каждый
        blocks = [ciphertext[i:i+self.block_size] for i in range(0, len(ciphertext), self.block_size)]
        plaintext = b''.join([self.cipher.decrypt(block) for block in blocks])
        
        # Убираем padding
        plaintext = unpad(plaintext, self.block_size)
        
        return plaintext
