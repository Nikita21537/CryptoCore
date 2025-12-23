import struct
from typing import List


# Вспомогательные функции для операций с битами
def rotate_right(x: int, n: int, bits: int = 32) -> int:

    return ((x >> n) | (x << (bits - n))) & ((1 << bits) - 1)


def rotate_left(x: int, n: int, bits: int = 32) -> int:

    return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)


def shift_right(x: int, n: int) -> int:

    return x >> n


def bytes_to_words(data: bytes, word_size: int = 4) -> List[int]:

    return [int.from_bytes(data[i:i + word_size], 'big')
            for i in range(0, len(data), word_size)]


def words_to_bytes(words: List[int], word_size: int = 4) -> bytes:

    return b''.join(word.to_bytes(word_size, 'big') for word in words)


def pad_message(message: bytes, block_size: int, length_size: int = 8) -> bytes:

    original_length = len(message) * 8  # длина в битах
    message += b'\x80'  # добавляем бит '1'

    # Добавляем нули до (block_size - length_size - 1) байт от конца
    while (len(message) % block_size) != (block_size - length_size):
        message += b'\x00'

    # Добавляем длину оригинального сообщения
    message += original_length.to_bytes(length_size, 'big')

    return message