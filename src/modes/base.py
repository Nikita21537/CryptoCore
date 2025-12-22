from abc import ABC, abstractmethod
from Crypto.Cipher import AES
from typing import Optional

# Import CSPRNG
try:
    from src.cryptocore.csprng import generate_iv, is_key_weak
except ImportError:
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from csprng import generate_iv, is_key_weak


class CipherMode(ABC):


    def __init__(self, key: bytes, iv: Optional[bytes] = None, mode_name: str = ""):
        self.key = key
        self.mode_name = mode_name

        # Warn about weak keys
        if is_key_weak(key):
            print(f"[WARNING] Using a potentially weak key!", file=sys.stderr)

        if iv is None:
            self.iv = generate_iv()  # Используем CSPRNG для генерации IV
        else:
            self.iv = iv

        # Базовый AES объект для примитивных операций
        self._aes = AES.new(self.key, AES.MODE_ECB)

    @abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:

        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:

        pass

    @property
    def requires_padding(self) -> bool:

        return True

    @property
    def iv_size(self) -> int:

        return 16

    def get_iv_hex(self) -> str:

        return self.iv.hex()