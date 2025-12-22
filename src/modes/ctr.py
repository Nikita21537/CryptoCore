from .base import CipherMode


class CTRMode(CipherMode):
    

    def __init__(self, key: bytes, iv: bytes = None):
        super().__init__(key, iv, "CTR")
        # В CTR IV используется как начальное значение счетчика
        if iv:
            self.counter = int.from_bytes(iv, 'big')
        else:
            self.counter = int.from_bytes(os.urandom(16), 'big')

    @property
    def requires_padding(self) -> bool:
        return False

    def _increment_counter(self):

        # Увеличиваем счетчик на 1, оборачивая при переполнении
        self.counter = (self.counter + 1) % (2 ** 128)

    def encrypt(self, plaintext: bytes) -> bytes:

        ciphertext = b''
        current_counter = self.counter

        for i in range(0, len(plaintext), 16):
            # Преобразуем счетчик в байты
            counter_bytes = current_counter.to_bytes(16, 'big')

            # Шифруем счетчик
            keystream_block = self._aes.encrypt(counter_bytes)

            # Берем нужное количество байт из keystream
            chunk_size = min(16, len(plaintext) - i)
            chunk = plaintext[i:i + chunk_size]

            # XOR с keystream
            encrypted_chunk = bytes(a ^ b for a, b in zip(chunk, keystream_block[:chunk_size]))
            ciphertext += encrypted_chunk

            # Инкрементируем счетчик
            current_counter = (current_counter + 1) % (2 ** 128)

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:

        return self.encrypt(ciphertext)  # CTR симметричен