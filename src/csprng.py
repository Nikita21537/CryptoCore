import os
import sys
from typing import Optional


class CSPRNGError(Exception):

    pass


def generate_random_bytes(num_bytes: int) -> bytes:

    if num_bytes <= 0:
        raise ValueError(f"num_bytes must be positive, got {num_bytes}")

    try:
        # Use os.urandom() which is cryptographically secure on most platforms
        # It uses /dev/urandom on Unix-like systems and CryptGenRandom on Windows
        return os.urandom(num_bytes)
    except Exception as e:
        raise CSPRNGError(f"Failed to generate random bytes: {e}")


def is_key_weak(key: bytes) -> bool:
    """Check if a key appears to be weak."""
    if len(key) == 0:
        return False

    # Check for all zeros
    if all(b == 0 for b in key):
        return True

    # Check for all ones (0xFF)
    if all(b == 0xFF for b in key):
        return True

    # Check for simple sequential patterns
    # Increasing sequence (0, 1, 2, 3, ...)
    is_increasing = all(key[i] == (key[i - 1] + 1) % 256 for i in range(1, len(key)))
    # Decreasing sequence (0xFF, 0xFE, 0xFD, ...)
    is_decreasing = all(key[i] == (key[i - 1] - 1) % 256 for i in range(1, len(key)))

    if is_increasing or is_decreasing:
        return True

    # Check for repeated bytes (AAAAAAAA...)
    if all(b == key[0] for b in key[1:]):
        return True

    # Check for repeated patterns (ABABAB...)
    if len(key) % 2 == 0:
        pattern = key[:2]
        repeats_correctly = all(key[i:i + 2] == pattern for i in range(0, len(key), 2))
        if repeats_correctly:
            return True

    return False


def generate_aes_key() -> bytes:

    return generate_random_bytes(16)


def generate_iv() -> bytes:

    return generate_random_bytes(16)


def generate_salt(length: int = 16) -> bytes:

    if length <= 0:
        raise ValueError(f"Salt length must be positive, got {length}")
    return generate_random_bytes(length)


def print_key_info(key: bytes, source: str = "generated") -> None:

    key_hex = key.hex()

    print(f"[INFO] {source.capitalize()} key: {key_hex}")

    # Calculate and show some statistics
    ones_count = sum(bin(b).count('1') for b in key)
    total_bits = len(key) * 8
    ones_percentage = (ones_count / total_bits) * 100

    print(f"[INFO] Key statistics: {ones_count}/{total_bits} bits set to 1 ({ones_percentage:.1f}%)")

    # Warn if key looks weak
    if is_key_weak(key):
        print(f"[WARNING] The provided key appears to be weak!", file=sys.stderr)
        print(f"[WARNING] Consider using a more random key for better security.", file=sys.stderr)