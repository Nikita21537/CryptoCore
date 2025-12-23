from typing import Optional


def xor_bytes(a: bytes, b: bytes) -> bytes:

    if len(a) != len(b):
        raise ValueError(f"Bytes must be same length: {len(a)} != {len(b)}")

    return bytes(x ^ y for x, y in zip(a, b))


def pad_key(key: bytes, block_size: int) -> bytes:

    if len(key) > block_size:
        # Если ключ длиннее блока - хешируем его
        from src.hash import SHA256
        key = SHA256().hash(key)

    if len(key) < block_size:
        # Если ключ короче блока - дополняем нулями
        key = key + b'\x00' * (block_size - len(key))

    return key


def parse_hmac_file(filepath: str) -> tuple[str, Optional[str]]:

    with open(filepath, 'r') as f:
        content = f.read().strip()

    parts = content.split()

    if not parts:
        raise ValueError(f"Empty HMAC file: {filepath}")

    hmac_value = parts[0].strip()
    filename = parts[1] if len(parts) > 1 else None

    # Проверяем формат HMAC (64 hex символа для SHA-256)
    if len(hmac_value) != 64 or not all(c in '0123456789abcdef' for c in hmac_value.lower()):
        raise ValueError(f"Invalid HMAC format in file: {filepath}")

    return hmac_value, filename