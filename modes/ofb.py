from src.modes.mode_interface import ModeInterface

class OFBCipher(ModeInterface):
    def __init__(self, cipher, block_size=16, rng_function=None):
        self.cipher = cipher
        self.block_size = block_size
        self.rng_function = rng_function

    def encrypt(self, plaintext):
        if not self.rng_function:
            raise RuntimeError("RNG function not provided for OFB mode")
            
        iv = self.rng_function(self.block_size)
        ciphertext = b''
        keystream = iv
        
        for i in range(0, len(plaintext), self.block_size):
            block = plaintext[i:i+self.block_size]
            encrypted_keystream = self.cipher.encrypt(keystream)
            
            # XOR с открытым текстом
            encrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_keystream[:len(block)]))
            ciphertext += encrypted_block
            
            # Для следующего блока используем зашифрованный keystream
            keystream = encrypted_keystream

        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        plaintext = b''
        keystream = iv
        
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i+self.block_size]
            encrypted_keystream = self.cipher.encrypt(keystream)
            
            # XOR с шифротекстом
            decrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_keystream[:len(block)]))
            plaintext += decrypted_block
            
            # Для следующего блока используем зашифрованный keystream
            keystream = encrypted_keystream

        return plaintext
