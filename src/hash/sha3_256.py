import struct
from typing import List


class SHA3_256:


    # Keccak constants
    _RC = [
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
        0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
        0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
        0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
        0x8000000000008080, 0x0000000080000001, 0x8000000080008008
    ]

    # Rotation offsets
    _RHO = [
        [0, 36, 3, 41, 18],
        [1, 44, 10, 45, 2],
        [62, 6, 43, 15, 61],
        [28, 55, 25, 21, 56],
        [27, 20, 39, 8, 14]
    ]

    # Pi permutation
    _PI = [
        [0, 3, 1, 4, 2],
        [1, 4, 2, 0, 3],
        [2, 0, 3, 1, 4],
        [3, 1, 4, 2, 0],
        [4, 2, 0, 3, 1]
    ]

    def __init__(self):

        self.reset()

    def reset(self):

        # State is 5x5 matrix of 64-bit words
        self._state = [[0] * 5 for _ in range(5)]
        self._buffer = bytearray()
        self._total_length = 0

        # SHA3-256 parameters
        self._rate = 1088 // 8  # 136 bytes (1088 bits)
        self._capacity = 512  # bits
        self._output_length = 256 // 8  # 32 bytes

    @staticmethod
    def _rotate_left_64(x: int, n: int) -> int:

        n %= 64
        return ((x << n) | (x >> (64 - n))) & ((1 << 64) - 1)

    def _keccak_f(self):

        for round_ in range(24):
            # θ step
            C = [0] * 5
            D = [0] * 5

            for x in range(5):
                C[x] = (self._state[x][0] ^ self._state[x][1] ^
                        self._state[x][2] ^ self._state[x][3] ^
                        self._state[x][4])

            for x in range(5):
                D[x] = C[(x - 1) % 5] ^ self._rotate_left_64(C[(x + 1) % 5], 1)

            for x in range(5):
                for y in range(5):
                    self._state[x][y] ^= D[x]

            # ρ and π steps
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    B[y][(2 * x + 3 * y) % 5] = self._rotate_left_64(
                        self._state[x][y], self._RHO[x][y]
                    )

            # χ step
            for x in range(5):
                for y in range(5):
                    self._state[x][y] = B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y])

            # ι step
            self._state[0][0] ^= self._RC[round_]

    def _absorb(self):

        # Pad buffer to rate if needed
        while len(self._buffer) < self._rate:
            self._buffer.append(0)

        # XOR buffer into state
        block = bytes(self._buffer[:self._rate])
        self._buffer = self._buffer[self._rate:]

        # Convert block to state
        for i in range(self._rate // 8):
            x = i % 5
            y = i // 5
            word = struct.unpack('<Q', block[i * 8:(i + 1) * 8])[0]
            self._state[x][y] ^= word

    def _pad(self, suffix: int) -> bytes:

        # SHA3 uses padding: 0x06 = 0110 (suffix 01 + 10*1)
        # But we implement general padding

        P = self._buffer

        # Add suffix bits
        # For SHA3-256: suffix bits are 0x06 (0110 in binary)
        # 01 for SHA3 domain separation + 10*1 pad pattern
        if suffix & 1:
            P[-1] ^= 0x80  # Last byte, most significant bit

        # Add pad10*1 pattern
        # Find first zero byte from the end
        pad_pos = self._rate - len(P)
        if pad_pos == 1:
            # Special case: need to add a whole new block
            P.append(0x86)  # 10000110
            while len(P) < self._rate:
                P.append(0x00)
            P[-1] ^= 0x01  # Last bit of pad10*1
        else:
            # Normal padding
            P.append(0x06)  # 00000110
            while len(P) < self._rate - 1:
                P.append(0x00)
            P.append(0x80)  # 10000000

        return bytes(P)

    def update(self, data: bytes):

        if not data:
            return

        self._total_length += len(data)
        self._buffer.extend(data)

        # Process complete blocks
        while len(self._buffer) >= self._rate:
            self._absorb()
            self._keccak_f()

    def digest(self) -> bytes:

        # Apply SHA3 padding (0x06 suffix)
        padded = self._pad(0x06)

        # Absorb padded message
        self._buffer = bytearray(padded)
        self._absorb()
        self._keccak_f()

        # Squeeze output
        output = bytearray()
        while len(output) < self._output_length:
            # Extract from state
            for i in range(self._rate // 8):
                if len(output) >= self._output_length:
                    break
                x = i % 5
                y = i // 5
                output.extend(struct.pack('<Q', self._state[x][y]))

            if len(output) < self._output_length:
                self._keccak_f()

        # Reset for potential reuse
        self.reset()

        return bytes(output[:self._output_length])

    def hexdigest(self) -> str:

        return self.digest().hex()

    @classmethod
    def hash(cls, data: bytes) -> bytes:

        sha3 = cls()
        sha3.update(data)
        return sha3.digest()

    @classmethod
    def hash_hex(cls, data: bytes) -> str:

        return cls.hash(data).hex()