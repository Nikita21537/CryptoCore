from .base import CipherMode
from Crypto.Util.Padding import pad, unpad


class CBCMode(CipherMode):
    

    def __init__(self, key: bytes, iv: bytes = None):
        super().__init__(key, iv, "CBC")

    @property
    def requires_padding(self) -> bool:
        return True

    def encrypt(self, plaintext: bytes) -> bytes:

        # Добавляем паддинг
        padded_data = pad(plaintext, AES.block_size)

        # Разбиваем на блоки
        blocks = [padded_data[i:i + 16] for i in range(0, len(padded_data), 16)]

        ciphertext = b''
        previous_block = self.iv

        for block in blocks:
            # XOR с предыдущим зашифрованным блоком (или IV для первого)
            xor_block = bytes(a ^ b for a, b in zip(block, previous_block))

            # Шифруем блок
            encrypted_block = self._aes.encrypt(xor_block)
            ciphertext += encrypted_block
            previous_block = encrypted_block

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:

        if len(ciphertext) % 16 != 0:
            raise ValueError("Ciphertext length must be multiple of block size")

        # Разбиваем на блоки
        blocks = [ciphertext[i:i + 16] for i in range(0, len(ciphertext), 16)]

        plaintext = b''
        previous_block = self.iv

        for block in blocks:
            # Расшифровываем блок
            decrypted_block = self._aes.decrypt(block)

            # XOR с предыдущим зашифрованным блоком
            plain_block = bytes(a ^ b for a, b in zip(decrypted_block, previous_block))
            plaintext += plain_block

            previous_block = block

        # Убираем паддинг
        return unpad(plaintext, AES.block_size)