from abc import ABC, abstractmethod
from Crypto.Cipher import AES
from typing import Optional
import sys

# Правильный импорт CSPRNG функций
try:
    # Пробуем импортировать напрямую из csprng
    from src.csprng import generate_iv, is_key_weak
except ImportError:
    # Fallback для случаев когда src не в пути
    import os

    # Добавляем родительскую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        from csprng import generate_iv, is_key_weak
    except ImportError:
        # Если всё ещё не получается, создаем заглушки
        import os as os_module


        def generate_iv():
            return os_module.urandom(16)


        def is_key_weak(key):
            # Простая проверка на слабые ключи
            if len(key) < 16:
                return False
            # Проверка на все нули
            if all(b == 0 for b in key):
                return True
            # Проверка на все 0xFF
            if all(b == 0xFF for b in key):
                return True
            # Проверка на последовательные байты
            is_sequential = all(key[i] == i % 256 for i in range(len(key)))
            if is_sequential:
                return True
            return False


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