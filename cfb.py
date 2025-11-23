import os
from src.modes.mode_interface import ModeInterface

class CFBCipher(ModeInterface):
    def __init__(self, cipher, block_size=16):
        self.cipher = cipher
        self.block_size = block_size

    def encrypt(self, plaintext):
        iv = os.urandom(self.block_size)
        ciphertext = b''
        feedback = iv
        
        for i in range(0, len(plaintext), self.block_size):
            block = plaintext[i:i+self.block_size]
            encrypted_feedback = self.cipher.encrypt(feedback)
            
            # XOR с открытым текстом
            encrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_feedback[:len(block)]))
            ciphertext += encrypted_block
            
            # Для следующего блока используем зашифрованный блок как feedback
            if len(block) == self.block_size:
                feedback = encrypted_block
            else:
                # Для последнего неполного блока используем начало зашифрованного feedback
                feedback = encrypted_feedback

        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        plaintext = b''
        feedback = iv
        
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i+self.block_size]
            encrypted_feedback = self.cipher.encrypt(feedback)
            
            # XOR с шифротекстом
            decrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_feedback[:len(block)]))
            plaintext += decrypted_block
            
            # Для следующего блока используем текущий блок шифротекста как feedback
            feedback = block

        return plaintext
