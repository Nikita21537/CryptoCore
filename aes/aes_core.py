from Crypto.Cipher import AES


class AES128:
    """Класс для работы с AES-128"""

    def __init__(self, key):
        if len(key) != 16:
            raise ValueError("Key must be 16 bytes for AES-128")
        self.key = key
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt_block(self, block):
        """Шифрование одного блока"""
        if len(block) != 16:
            raise ValueError("Block must be 16 bytes")
        return self.cipher.encrypt(block)

    def decrypt_block(self, block):
        """Дешифрование одного блока"""
        if len(block) != 16:
            raise ValueError("Block must be 16 bytes")
        return self.cipher.decrypt(block)
