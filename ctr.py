mport os
from src.modes.mode_interface import ModeInterface

class CTRCipher(ModeInterface):
    def __init__(self, cipher, block_size=16):
        self.cipher = cipher
        self.block_size = block_size

    def encrypt(self, plaintext):
        iv = os.urandom(self.block_size)
        ciphertext = b''
        
        for i in range(0, len(plaintext), self.block_size):
            block = plaintext[i:i+self.block_size]
            
            # Создаем счетчик из IV + номер блока
            counter = self._increment_counter(iv, i // self.block_size)
            encrypted_counter = self.cipher.encrypt(counter)
            
            # XOR с открытым текстом
            encrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_counter[:len(block)]))
            ciphertext += encrypted_block

        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        plaintext = b''
        
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i+self.block_size]
            
            # Создаем счетчик из IV + номер блока
            counter = self._increment_counter(iv, i // self.block_size)
            encrypted_counter = self.cipher.encrypt(counter)
            
            # XOR с шифротекстом
            decrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_counter[:len(block)]))
            plaintext += decrypted_block

        return plaintext

    def _increment_counter(self, counter, increment):
        """Инкрементирует счетчик на заданное значение"""
        counter_int = int.from_bytes(counter, byteorder='big')
        counter_int += increment
        return counter_int.to_bytes(self.block_size, byteorder='big')
