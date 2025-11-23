import os
from Crypto.Util.Padding import pad, unpad
from src.modes.mode_interface import ModeInterface

class CBCCipher(ModeInterface):
    def __init__(self, cipher, block_size=16):
        self.cipher = cipher
        self.block_size = block_size

    def encrypt(self, plaintext):
        iv = os.urandom(self.block_size)
        blocks = [plaintext[i:i+self.block_size] for i in range(0, len(plaintext), self.block_size)]
        
        ciphertext = b''
        prev_block = iv
        
        for block in blocks:
            if len(block) < self.block_size:
                block = pad(block, self.block_size)
            xored = bytes(a ^ b for a, b in zip(block, prev_block))
            encrypted_block = self.cipher.encrypt(xored)
            ciphertext += encrypted_block
            prev_block = encrypted_block
        
        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        
        blocks = [ciphertext[i:i+self.block_size] for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext = b''
        prev_block = iv
        
        for block in blocks:
            decrypted_block = self.cipher.decrypt(block)
            xored = bytes(a ^ b for a, b in zip(decrypted_block, prev_block))
            plaintext += xored
            prev_block = block
        
        # Убираем padding только для последнего блока
        try:
            plaintext = unpad(plaintext, self.block_size)
        except ValueError:
            # Если padding некорректен, оставляем как есть
            pass
            
        return plaintext
