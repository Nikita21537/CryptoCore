from Crypto.Cipher import AES
from typing import Union


class PKCS7Padding:


    @staticmethod
    def pad(data: bytes, block_size: int = 16) -> bytes:

        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    @staticmethod
    def unpad(data: bytes) -> bytes:
        
        if not data:
            return data
        padding_length = data[-1]
        # Validate padding
        if padding_length < 1 or padding_length > len(data):
            raise ValueError("Invalid padding")
        if data[-padding_length:] != bytes([padding_length] * padding_length):
            raise ValueError("Invalid padding")
        return data[:-padding_length]


class AES_ECB:


    def __init__(self, key: bytes):

        if len(key) != 16:
            raise ValueError(f"AES-128 requires 16-byte key, got {len(key)} bytes")
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes:

        # Pad the plaintext
        padded_plaintext = PKCS7Padding.pad(plaintext, AES.block_size)

        # Create cipher object
        cipher = AES.new(self.key, AES.MODE_ECB)

        # Encrypt block by block
        ciphertext = cipher.encrypt(padded_plaintext)
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:

        if len(ciphertext) % AES.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")

        # Create cipher object
        cipher = AES.new(self.key, AES.MODE_ECB)

        # Decrypt
        padded_plaintext = cipher.decrypt(ciphertext)

        # Remove padding
        plaintext = PKCS7Padding.unpad(padded_plaintext)
        return plaintext