from .base import CipherMode


class OFBMode(CipherMode):


    def __init__(self, key: bytes, iv: bytes = None):
        super().__init__(key, iv, "OFB")

    @property
    def requires_padding(self) -> bool:
        return False

    def encrypt(self, plaintext: bytes) -> bytes:

        ciphertext = b''
        keystream_state = self.iv

        # Генерируем keystream
        for i in range(0, len(plaintext), 16):
            # Шифруем текущее состояние для получения keystream блока
            keystream_block = self._aes.encrypt(keystream_state)

            # Берем нужное количество байт из keystream
            chunk_size = min(16, len(plaintext) - i)
            chunk = plaintext[i:i + chunk_size]

            # XOR с keystream
            encrypted_chunk = bytes(a ^ b for a, b in zip(chunk, keystream_block[:chunk_size]))
            ciphertext += encrypted_chunk

            # Обновляем состояние для следующего блока
            keystream_state = keystream_block

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
       
        return self.encrypt(ciphertext)  # OFB симметричен