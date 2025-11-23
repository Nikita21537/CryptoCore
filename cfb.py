from Crypto.Util.Padding import pad, unpad
from src.modes.mode_interface import ModeInterface

class CBCCipher(ModeInterface):
    def __init__(self, cipher, block_size=16, rng_function=None):
        self.cipher = cipher
        self.block_size = block_size
        self.rng_function = rng_function

    def encrypt(self, plaintext):
        if not self.rng_function:
            raise RuntimeError("RNG function not provided for CBC mode")
            
        iv = self.rng_function(self.block_size)
        plaintext = pad(plaintext, self.block_size)
        
        blocks = [plaintext[i:i+self.block_size] for i in range(0, len(plaintext), self.block_size)]
        
        ciphertext = b''
        prev_block = iv
        
        for block in blocks:
            # XOR с предыдущим блоком шифротекста (или IV для первого блока)
            xored = bytes(a ^ b for a, b in zip(block, prev_block))
            encrypted_block = self.cipher.encrypt(xored)
            ciphertext += encrypted_block
            prev_block = encrypted_block
        
        return iv + ciphertext

    def decrypt(self, ciphertext):
        # Извлекаем IV из начала шифротекста
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        
        blocks = [ciphertext[i:i+self.block_size] for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext = b''
        prev_block = iv
        
        for block in blocks:
            decrypted_block = self.cipher.decrypt(block)
            # XOR с предыдущим блоком шифротекста (или IV для первого блока)
            xored = bytes(a ^ b for a, b in zip(decrypted_block, prev_block))
            plaintext += xored
            prev_block = block
        
        # Убираем padding
        plaintext = unpad(plaintext, self.block_size)
        
        return plaintext
