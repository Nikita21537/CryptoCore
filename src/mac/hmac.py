from typing import Union
from src.cryptocore.hash import SHA256
from .utils import xor_bytes


class HMAC:


    # Константы для HMAC
    IPAD = 0x36  # inner pad value
    OPAD = 0x5C  # outer pad value

    def __init__(self, key: Union[bytes, str], hash_algorithm: str = 'sha256'):

        if isinstance(key, str):
            # Преобразуем hex строку в байты
            key = bytes.fromhex(key)

        self.hash_algorithm = hash_algorithm.lower()

        if self.hash_algorithm != 'sha256':
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}. Only 'sha256' is supported.")

        # Определяем размер блока и хеш-функцию
        self.block_size = 64  # 64 bytes for SHA-256
        self.hash_func = SHA256

        # Обрабатываем ключ согласно RFC 2104
        self.key = self._process_key(key)

    def _process_key(self, key: bytes) -> bytes:

        if len(key) > self.block_size:
            # Хешируем ключ если он длиннее блока
            key = self.hash_func().hash(key)

        if len(key) < self.block_size:
            # Дополняем нулями если ключ короче блока
            key = key + b'\x00' * (self.block_size - len(key))

        return key

    def compute(self, message: bytes) -> bytes:

        # Создаем inner и outer pad
        ipad = xor_bytes(self.key, bytes([self.IPAD] * self.block_size))
        opad = xor_bytes(self.key, bytes([self.OPAD] * self.block_size))

        # Внутренний хеш: H((K ⊕ ipad) || message)
        inner_hash = self.hash_func().hash(ipad + message)

        # Внешний хеш: H((K ⊕ opad) || inner_hash)
        outer_hash = self.hash_func().hash(opad + inner_hash)

        return outer_hash

    def compute_hex(self, message: bytes) -> str:

        return self.compute(message).hex()

    def verify(self, message: bytes, hmac: Union[bytes, str]) -> bool:

        computed = self.compute(message)

        if isinstance(hmac, str):
            expected = bytes.fromhex(hmac)
        else:
            expected = hmac

        # Константное время сравнения для предотвращения timing attacks
        return self._constant_time_compare(computed, expected)

    @staticmethod
    def _constant_time_compare(a: bytes, b: bytes) -> bool:

        if len(a) != len(b):
            return False

        result = 0
        for x, y in zip(a, b):
            result |= x ^ y

        return result == 0

    @classmethod
    def hmac_sha256(cls, key: bytes, message: bytes) -> bytes:

        return cls(key, 'sha256').compute(message)

    @classmethod
    def hmac_sha256_hex(cls, key: bytes, message: bytes) -> str:

        return cls(key, 'sha256').compute(message).hex()


class HMACStream:


    def __init__(self, key: Union[bytes, str], hash_algorithm: str = 'sha256'):

        self.hmac = HMAC(key, hash_algorithm)

        # Инициализируем внутренний и внешний хеш контексты
        self.inner_hash = SHA256()
        self.outer_hash = SHA256()

        # Подготавливаем ключи
        ipad = xor_bytes(self.hmac.key, bytes([HMAC.IPAD] * self.hmac.block_size))
        opad = xor_bytes(self.hmac.key, bytes([HMAC.OPAD] * self.hmac.block_size))

        # Инициализируем inner hash с ipad
        self.inner_hash.update(ipad)
        # Инициализируем outer hash с opad
        self.outer_hash.update(opad)

    def update(self, data: bytes):

        self.inner_hash.update(data)

    def finalize(self) -> bytes:

        # Завершаем inner hash
        inner_digest = self.inner_hash.digest()

        # Вычисляем outer hash: H(opad || inner_hash)
        self.outer_hash.update(inner_digest)
        outer_digest = self.outer_hash.digest()

        return outer_digest

    def finalize_hex(self) -> str:

        return self.finalize().hex()