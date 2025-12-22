import struct
from typing import List
from .utils import rotate_right, shift_right


class SHA256:


    # Initial hash values (first 32 bits of fractional parts of square roots of first 8 primes)
    _H0 = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    # Round constants (first 32 bits of fractional parts of cube roots of first 64 primes)
    _K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    def __init__(self):

        self.reset()

    def reset(self):

        self._hash = self._H0[:]
        self._message_length = 0
        self._buffer = bytearray()

    @staticmethod
    def _sigma0(x: int) -> int:

        return rotate_right(x, 7) ^ rotate_right(x, 18) ^ shift_right(x, 3)

    @staticmethod
    def _sigma1(x: int) -> int:

        return rotate_right(x, 17) ^ rotate_right(x, 19) ^ shift_right(x, 10)

    @staticmethod
    def _Sigma0(x: int) -> int:

        return rotate_right(x, 2) ^ rotate_right(x, 13) ^ rotate_right(x, 22)

    @staticmethod
    def _Sigma1(x: int) -> int:

        return rotate_right(x, 6) ^ rotate_right(x, 11) ^ rotate_right(x, 25)

    @staticmethod
    def _Ch(x: int, y: int, z: int) -> int:

        return (x & y) ^ (~x & z)

    @staticmethod
    def _Maj(x: int, y: int, z: int) -> int:

        return (x & y) ^ (x & z) ^ (y & z)

    def _process_block(self, block: bytes):

        if len(block) != 64:
            raise ValueError(f"Block must be 64 bytes, got {len(block)}")

        # Prepare message schedule
        w = [0] * 64

        # First 16 words are the block itself
        for i in range(16):
            w[i] = struct.unpack('>I', block[i * 4:(i + 1) * 4])[0]

        # Extend to 64 words
        for i in range(16, 64):
            s0 = self._sigma0(w[i - 15])
            s1 = self._sigma1(w[i - 2])
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

        # Initialize working variables
        a, b, c, d, e, f, g, h = self._hash

        # Compression function main loop
        for i in range(64):
            S1 = self._Sigma1(e)
            ch = self._Ch(e, f, g)
            temp1 = (h + S1 + ch + self._K[i] + w[i]) & 0xFFFFFFFF
            S0 = self._Sigma0(a)
            maj = self._Maj(a, b, c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        # Update hash values
        self._hash[0] = (self._hash[0] + a) & 0xFFFFFFFF
        self._hash[1] = (self._hash[1] + b) & 0xFFFFFFFF
        self._hash[2] = (self._hash[2] + c) & 0xFFFFFFFF
        self._hash[3] = (self._hash[3] + d) & 0xFFFFFFFF
        self._hash[4] = (self._hash[4] + e) & 0xFFFFFFFF
        self._hash[5] = (self._hash[5] + f) & 0xFFFFFFFF
        self._hash[6] = (self._hash[6] + g) & 0xFFFFFFFF
        self._hash[7] = (self._hash[7] + h) & 0xFFFFFFFF

    def update(self, data: bytes):

        if not data:
            return

        self._message_length += len(data)
        self._buffer.extend(data)

        # Process complete blocks
        while len(self._buffer) >= 64:
            block = bytes(self._buffer[:64])
            self._process_block(block)
            self._buffer = self._buffer[64:]

    def _pad(self):

        # Start with the buffer
        message = bytes(self._buffer)

        # Add bit '1'
        message += b'\x80'

        # Calculate padding length
        # Total length after padding must be 64 bytes (512 bits) * n
        # The last 8 bytes (64 bits) store the original message length in bits
        message_length_bits = self._message_length * 8

        # Add zeros
        while (len(message) % 64) != 56:
            message += b'\x00'

        # Add message length (big-endian, 64 bits)
        message += struct.pack('>Q', message_length_bits)

        return message

    def digest(self) -> bytes:

        # Apply padding
        padded_message = self._pad()

        # Process any remaining blocks
        temp_hash = self._hash[:]

        # Process padded message
        for i in range(0, len(padded_message), 64):
            # Temporarily set hash to initial for block processing
            self._hash = self._H0[:]
            self._process_block(padded_message[i:i + 64])
            # Update temp hash
            for j in range(8):
                temp_hash[j] = (temp_hash[j] + self._hash[j]) & 0xFFFFFFFF
            self._hash = temp_hash[:]

        # Convert hash to bytes
        digest_bytes = b''.join(struct.pack('>I', h) for h in self._hash)

        # Reset for potential reuse
        self.reset()

        return digest_bytes

    def hexdigest(self) -> str:

        return self.digest().hex()

    @classmethod
    def hash(cls, data: bytes) -> bytes:

        sha256 = cls()
        sha256.update(data)
        return sha256.digest()

    @classmethod
    def hash_hex(cls, data: bytes) -> str:

        return cls.hash(data).hex()