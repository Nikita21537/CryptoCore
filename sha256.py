import struct
import binascii

class SHA256:
    def __init__(self):
        # Initialize hash values (first 32 bits of fractional parts of square roots of first 8 primes)
        self.h = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        
        # Initialize round constants (first 32 bits of fractional parts of cube roots of first 64 primes)
        self.k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]
        
        self.message_length = 0
        self.chunk = b''

    @staticmethod
    def _right_rotate(n, b):
        return ((n >> b) | (n << (32 - b))) & 0xffffffff

    def _padding(self, message):
        """SHA-256 padding"""
        length = len(message)
        self.message_length += length
        
        # Pre-processing: padding the message
        message += b'\x80'
        while (len(message) % 64) != 56:
            message += b'\x00'
        
        # Append original length in bits as 64-bit big-endian integer
        message += struct.pack('>Q', self.message_length * 8)
        
        return message

    def _process_block(self, block):
        """Process one 512-bit block"""
        if len(block) != 64:
            raise ValueError("Block must be exactly 64 bytes")
        
        # Break chunk into sixteen 32-bit big-endian words
        w = [0] * 64
        for i in range(16):
            w[i] = struct.unpack('>I', block[i*4:(i+1)*4])[0]
        
        # Extend the sixteen 32-bit words into sixty-four 32-bit words
        for i in range(16, 64):
            s0 = self._right_rotate(w[i-15], 7) ^ self._right_rotate(w[i-15], 18) ^ (w[i-15] >> 3)
            s1 = self._right_rotate(w[i-2], 17) ^ self._right_rotate(w[i-2], 19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff
        
        # Initialize working variables
        a, b, c, d, e, f, g, h = self.h
        
        # Main loop
        for i in range(64):
            s1 = self._right_rotate(e, 6) ^ self._right_rotate(e, 11) ^ self._right_rotate(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h + s1 + ch + self.k[i] + w[i]) & 0xffffffff
            s0 = self._right_rotate(a, 2) ^ self._right_rotate(a, 13) ^ self._right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & 0xffffffff
            
            h = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff
        
        # Add compressed chunk to current hash value
        self.h[0] = (self.h[0] + a) & 0xffffffff
        self.h[1] = (self.h[1] + b) & 0xffffffff
        self.h[2] = (self.h[2] + c) & 0xffffffff
        self.h[3] = (self.h[3] + d) & 0xffffffff
        self.h[4] = (self.h[4] + e) & 0xffffffff
        self.h[5] = (self.h[5] + f) & 0xffffffff
        self.h[6] = (self.h[6] + g) & 0xffffffff
        self.h[7] = (self.h[7] + h) & 0xffffffff

    def update(self, message):
        """Update hash with message bytes"""
        self.chunk += message
        
        # Process complete 64-byte blocks
        while len(self.chunk) >= 64:
            block = self.chunk[:64]
            self._process_block(block)
            self.chunk = self.chunk[64:]
            self.message_length += 64

    def digest(self):
        """Return final hash digest"""
        # Process remaining bytes with padding
        padded = self._padding(self.chunk)
        
        for i in range(0, len(padded), 64):
            block = padded[i:i+64]
            self._process_block(block)
        
        # Produce final hash value
        return b''.join(struct.pack('>I', h) for h in self.h)

    def hexdigest(self):
        """Return final hash as hexadecimal string"""
        return binascii.hexlify(self.digest()).decode('ascii')

    def hash(self, message):
        """Convenience method to hash entire message at once"""
        self.update(message)
        return self.hexdigest()
