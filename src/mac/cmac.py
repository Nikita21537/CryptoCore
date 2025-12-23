from typing import Union
from src.modes import AES_ECB
from .utils import xor_bytes


class AESCMAC:


    BLOCK_SIZE = 16  # 128 bits for AES

    def __init__(self, key: Union[bytes, str]):

        if isinstance(key, str):
            key = bytes.fromhex(key)

        if len(key) != 16:
            raise ValueError(f"AES-CMAC requires 16-byte key, got {len(key)} bytes")

        self.key = key
        self.aes = AES_ECB(key)

        # Генерируем подключи
        self.subkey1, self.subkey2 = self._generate_subkeys()

    def _generate_subkeys(self) -> tuple[bytes, bytes]:

        # Шаг 1: L = AES(K, 0^128)
        zero_block = bytes([0] * self.BLOCK_SIZE)
        L = self.aes.encrypt(zero_block)

        # Шаг 2: Генерация K1
        K1 = self._left_shift(L)
        if L[0] & 0x80:  # Если старший бит L равен 1
            K1 = xor_bytes(K1, bytes.fromhex('00000000000000000000000000000087'))

        # Шаг 3: Генерация K2
        K2 = self._left_shift(K1)
        if K1[0] & 0x80:  # Если старший бит K1 равен 1
            K2 = xor_bytes(K2, bytes.fromhex('00000000000000000000000000000087'))

        return K1, K2

    @staticmethod
    def _left_shift(block: bytes) -> bytes:

        result = bytearray(16)
        carry = 0

        for i in range(15, -1, -1):
            new_carry = (block[i] & 0x80) >> 7
            result[i] = ((block[i] << 1) & 0xFF) | carry
            carry = new_carry

        return bytes(result)

    def compute(self, message: bytes) -> bytes:

        # Разбиваем сообщение на блоки
        blocks = []
        for i in range(0, len(message), self.BLOCK_SIZE):
            blocks.append(message[i:i + self.BLOCK_SIZE])

        # Обрабатываем последний блок
        if not blocks:
            # Пустое сообщение
            last_block = bytes([0] * self.BLOCK_SIZE)
            last_block = xor_bytes(last_block, self.subkey2)
            blocks = [last_block]
        elif len(blocks[-1]) == self.BLOCK_SIZE:
            # Полный последний блок
            blocks[-1] = xor_bytes(blocks[-1], self.subkey1)
        else:
            # Неполный последний блок - добавляем padding
            last_block = blocks[-1]
            padding_needed = self.BLOCK_SIZE - len(last_block)
            last_block = last_block + bytes([0x80] + [0] * (padding_needed - 1))
            blocks[-1] = xor_bytes(last_block, self.subkey2)

        # CBC-MAC вычисление
        ciphertext = bytes([0] * self.BLOCK_SIZE)  # IV = 0

        for block in blocks:
            ciphertext = xor_bytes(ciphertext, block)
            ciphertext = self.aes.encrypt(ciphertext)

        return ciphertext

    def compute_hex(self, message: bytes) -> str:

        return self.compute(message).hex()

    def verify(self, message: bytes, cmac: Union[bytes, str]) -> bool:

        computed = self.compute(message)

        if isinstance(cmac, str):
            expected = bytes.fromhex(cmac)
        else:
            expected = cmac

        # Константное время сравнения
        return self._constant_time_compare(computed, expected)

    @staticmethod
    def _constant_time_compare(a: bytes, b: bytes) -> bool:
        """Сравнение в константном времени."""
        if len(a) != len(b):
            return False

        result = 0
        for x, y in zip(a, b):
            result |= x ^ y

        return result == 0