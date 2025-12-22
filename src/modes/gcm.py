import struct
from typing import Optional
from Crypto.Cipher import AES
from src.cryptocore.csprng import generate_random_bytes


class AuthenticationError(Exception):

    pass


class GCM:


    # Irreducible polynomial for GF(2^128): x^128 + x^7 + x^2 + x + 1
    R = 0xE1000000000000000000000000000000
    BLOCK_SIZE = 16  # 128 bits

    def __init__(self, key: bytes, nonce: Optional[bytes] = None):
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Key must be 16, 24, or 32 bytes, got {len(key)}")

        self.key = key
        self.aes = AES.new(key, AES.MODE_ECB)

        # Generate random 12-byte nonce if not provided
        if nonce:
            self.nonce = nonce
        else:
            self.nonce = generate_random_bytes(12)

        # Precompute H = AES_K(0^128)
        self.H = self.aes.encrypt(b'\x00' * self.BLOCK_SIZE)
        self.H_int = int.from_bytes(self.H, 'big')

        # Precompute multiplication table for GHASH
        self.mul_table = self._precompute_mul_table()

    def _precompute_mul_table(self):

        table = {}

        # Precompute powers of H
        h = self.H_int
        for i in range(128):
            table[1 << i] = h
            # Multiply by x (left shift)
            if h & 1:
                h = (h >> 1) ^ self.R
            else:
                h = h >> 1

        return table

    def _mult_gf(self, x: int, y: int) -> int:

        z = 0
        for i in range(128):
            if (x >> i) & 1:
                z ^= self.mul_table.get(1 << i, 0)
        return z

    def _ghash(self, aad: bytes, ciphertext: bytes) -> int:

        # Prepare blocks
        y = 0

        # Process AAD
        aad_len = len(aad)
        for i in range(0, aad_len, self.BLOCK_SIZE):
            block = aad[i:i + self.BLOCK_SIZE]
            if len(block) < self.BLOCK_SIZE:
                block = block.ljust(self.BLOCK_SIZE, b'\x00')
            block_int = int.from_bytes(block, 'big')
            y = self._mult_gf(y ^ block_int, self.H_int)

        # Process ciphertext
        ciphertext_len = len(ciphertext)
        for i in range(0, ciphertext_len, self.BLOCK_SIZE):
            block = ciphertext[i:i + self.BLOCK_SIZE]
            if len(block) < self.BLOCK_SIZE:
                block = block.ljust(self.BLOCK_SIZE, b'\x00')
            block_int = int.from_bytes(block, 'big')
            y = self._mult_gf(y ^ block_int, self.H_int)

        # Process lengths (64 bits each)
        len_block = struct.pack('>QQ', aad_len * 8, ciphertext_len * 8)
        len_int = int.from_bytes(len_block, 'big')
        y = self._mult_gf(y ^ len_int, self.H_int)

        return y

    def _inc_counter(self, counter: bytes) -> bytes:

        if len(counter) != 16:
            raise ValueError("Counter must be 16 bytes")

        counter_int = int.from_bytes(counter, 'big')
        counter_low = counter_int & 0xFFFFFFFF
        counter_high = counter_int >> 32

        counter_low = (counter_low + 1) & 0xFFFFFFFF

        new_counter = (counter_high << 32) | counter_low
        return new_counter.to_bytes(16, 'big')

    def _generate_iv(self) -> bytes:

        if len(self.nonce) == 12:
            # GCM default: nonce || 0x00000001
            return self.nonce + b'\x00\x00\x00\x01'
        else:
            # GHASH for other nonce lengths
            # For simplicity, we only support 12-byte nonce
            raise ValueError("Only 12-byte nonce supported")

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:

        # Generate J0
        j0 = self._generate_iv()

        # Generate initial counter for encryption
        counter = self._inc_counter(j0)

        # Encrypt using CTR mode
        ciphertext = b''
        blocks = [plaintext[i:i + self.BLOCK_SIZE]
                 for i in range(0, len(plaintext), self.BLOCK_SIZE)]

        for block in blocks:
            # Encrypt counter to get keystream
            keystream = self.aes.encrypt(counter)

            # XOR with plaintext block
            if len(block) < self.BLOCK_SIZE:
                keystream = keystream[:len(block)]

            ciphertext_block = bytes(a ^ b for a, b in zip(block, keystream))
            ciphertext += ciphertext_block

            # Increment counter
            counter = self._inc_counter(counter)

        # Compute authentication tag
        s = self.aes.encrypt(j0)
        auth_tag_int = self._ghash(aad, ciphertext) ^ int.from_bytes(s, 'big')
        auth_tag = auth_tag_int.to_bytes(16, 'big')

        # Return: nonce + ciphertext + tag
        return self.nonce + ciphertext + auth_tag

    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:

        if len(data) < 28:  # min: 12 nonce + 0 ciphertext + 16 tag
            raise ValueError("Data too short for GCM format")

        # Extract components
        nonce = data[:12]
        tag = data[-16:]
        ciphertext = data[12:-16]

        # Verify authentication tag
        self.nonce = nonce  # Set nonce for tag calculation
        j0 = self._generate_iv()
        s = self.aes.encrypt(j0)
        computed_tag_int = self._ghash(aad, ciphertext) ^ int.from_bytes(s, 'big')
        computed_tag = computed_tag_int.to_bytes(16, 'big')

        if not self._constant_time_compare(computed_tag, tag):
            raise AuthenticationError("GCM authentication failed")

        # Decrypt using CTR mode
        counter = self._inc_counter(j0)
        plaintext = b''

        blocks = [ciphertext[i:i + self.BLOCK_SIZE]
                 for i in range(0, len(ciphertext), self.BLOCK_SIZE)]

        for block in blocks:
            keystream = self.aes.encrypt(counter)

            if len(block) < self.BLOCK_SIZE:
                keystream = keystream[:len(block)]

            plaintext_block = bytes(a ^ b for a, b in zip(block, keystream))
            plaintext += plaintext_block

            counter = self._inc_counter(counter)

        return plaintext

    @staticmethod
    def _constant_time_compare(a: bytes, b: bytes) -> bool:

        if len(a) != len(b):
            return False

        result = 0
        for x, y in zip(a, b):
            result |= x ^ y

        return result == 0