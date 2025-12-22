from .base import CipherMode


class CFBMode(CipherMode):
   

    def __init__(self, key: bytes, iv: bytes = None):
        super().__init__(key, iv, "CFB")

    @property
    def requires_padding(self) -> bool:
        return False

    def encrypt(self, plaintext: bytes) -> bytes:

        ciphertext = b''
        feedback = self.iv

        # Обрабатываем данные побайтово (как потоковый шифр)
        for i in range(0, len(plaintext)):
            # Шифруем feedback регистр
            encrypted_feedback = self._aes.encrypt(feedback)

            # XOR первого байта с открытым текстом
            cipher_byte = encrypted_feedback[0] ^ plaintext[i]
            ciphertext += bytes([cipher_byte])

            # Обновляем feedback регистр: сдвигаем и добавляем зашифрованный байт
            feedback = feedback[1:] + bytes([cipher_byte])

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:

        plaintext = b''
        feedback = self.iv

        for i in range(0, len(ciphertext)):
            # Шифруем feedback регистр
            encrypted_feedback = self._aes.encrypt(feedback)

            # XOR первого байта с шифротекстом
            plain_byte = encrypted_feedback[0] ^ ciphertext[i]
            plaintext += bytes([plain_byte])

            # Обновляем feedback регистр: сдвигаем и добавляем байт шифротекста
            feedback = feedback[1:] + bytes([ciphertext[i]])

        return plaintext