import os
import struct
from typing import Tuple
from src.ciphers.aes import AES

class AuthenticationError(Exception):
  
    pass

class GCM:
    def __init__(self, key: bytes, nonce: bytes = None):
     
        if len(key) not in (16, 24, 32):
            raise ValueError("Key must be 16, 24, or 32 bytes")
            
        self.aes = AES(key)
        self.key = key
        
        if nonce is None:
            self.nonce = os.urandom(12)
        else:
            self.nonce = nonce
            
        if len(self.nonce) != 12:
            raise ValueError("Nonce must be 12 bytes for this implementation")
            
        # Precompute H = E_K(0^128)
        self.H = self._aes_encrypt_block(bytes(16))
        
        # Precompute multiplication table for GHASH
        self._precompute_mul_table()
        
    def _aes_encrypt_block(self, block: bytes) -> bytes:
       
        return self.aes.encrypt(block)
    
    def _precompute_mul_table(self):
      
        self.M = [0] * 16
        self.M[0] = 0
        
        # M[1] = H
        self.M[1] = int.from_bytes(self.H, 'big')
        
        # M[i] = M[i-1] * x mod P
        for i in range(2, 16):
            self.M[i] = self._mult_gf2_128(self.M[i-1], self.M[1])
    
    def _mult_gf2_128(self, x: int, y: int) -> int:
        """
        Multiply two 128-bit integers in GF(2^128) modulo
        irreducible polynomial x^128 + x^7 + x^2 + x + 1.
        """
        z = 0
        v = y
        
        # Irreducible polynomial: x^128 + x^7 + x^2 + x + 1
        # In hexadecimal, the low 128 bits are: 0xE1 << 120
        # Actually it's: 0xE1000000000000000000000000000000 (128-bit)
        poly = 0xE1000000000000000000000000000000
        
        for i in range(127, -1, -1):
            if (x >> i) & 1:
                z ^= v
            # Multiply v by x
            if v & 1:
                v = (v >> 1) ^ poly
            else:
                v >>= 1
        return z
    
    def _ghash(self, aad: bytes, ciphertext: bytes) -> bytes:
        """
        Compute GHASH in GF(2^128).
        
        Args:
            aad: Associated Authenticated Data
            ciphertext: Ciphertext
            
        Returns:
            16-byte authentication tag
        """
        # Prepare blocks: len(AAD) || len(C)
        len_aad = len(aad) * 8  # bits
        len_c = len(ciphertext) * 8  # bits
        
        # Convert to 64-bit big-endian
        len_block = struct.pack('>QQ', len_aad, len_c)
        
        # Process AAD
        y = 0
        pos = 0
        
        # Process AAD in 16-byte blocks
        while pos < len(aad):
            block = aad[pos:pos+16]
            if len(block) < 16:
                block = block + bytes(16 - len(block))
            block_int = int.from_bytes(block, 'big')
            y ^= block_int
            y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
            pos += 16
        
        # Process ciphertext in 16-byte blocks
        pos = 0
        while pos < len(ciphertext):
            block = ciphertext[pos:pos+16]
            if len(block) < 16:
                block = block + bytes(16 - len(block))
            block_int = int.from_bytes(block, 'big')
            y ^= block_int
            y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
            pos += 16
        
        # Process length block
        len_int = int.from_bytes(len_block, 'big')
        y ^= len_int
        y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
        
        return y.to_bytes(16, 'big')
    
    def _gctr(self, icb: bytes, x: bytes) -> bytes:
        """
        GCTR function for counter mode encryption.
        
        Args:
            icb: Initial Counter Block
            x: Input to encrypt/decrypt
            
        Returns:
            Encrypted/decrypted output
        """
        if not x:
            return b''
        
        n = (len(x) + 15) // 16  # Number of 16-byte blocks
        y = b''
        cb = icb
        
        for i in range(n):
            # Encrypt counter block
            encrypted_cb = self._aes_encrypt_block(cb)
            
            # Get plaintext block
            start = i * 16
            end = min((i + 1) * 16, len(x))
            block = x[start:end]
            
            # XOR with encrypted counter
            if len(block) < 16:
                encrypted_cb = encrypted_cb[:len(block)]
            y_block = bytes(a ^ b for a, b in zip(block, encrypted_cb))
            y += y_block
            
            # Increment counter (last 32 bits as big-endian integer)
            if len(cb) == 16:
                counter = int.from_bytes(cb[12:], 'big')
                counter = (counter + 1) & 0xFFFFFFFF
                cb = cb[:12] + counter.to_bytes(4, 'big')
        
        return y
    
    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        """
        Encrypt plaintext using GCM.
        
        Args:
            plaintext: Data to encrypt
            aad: Associated Authenticated Data
            
        Returns:
            nonce (12 bytes) + ciphertext + tag (16 bytes)
        """
        # J0 = nonce || 0^31 || 1 if len(nonce) == 12, else GHASH(nonce || 0^(s) || len(nonce))
        if len(self.nonce) == 12:
            j0 = self.nonce + b'\x00\x00\x00\x01'
        else:
            # For non-12-byte nonce (simplified)
            s = 16 * ((len(self.nonce) + 15) // 16) - len(self.nonce)
            padded_nonce = self.nonce + bytes(s)
            len_nonce = (len(self.nonce) * 8).to_bytes(16, 'big')
            j0 = self._ghash(padded_nonce + len_nonce, b"")
        
        # Generate initial counter block
        icb = j0
        
        # Encrypt plaintext in counter mode
        ciphertext = self._gctr(icb, plaintext)
        
        # Compute authentication tag
        s = self._ghash(aad, ciphertext)
        t = self._gctr(j0, s)
        
        return self.nonce + ciphertext + t
    
    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:
        """
        Decrypt and verify GCM data.
        
        Args:
            data: Combined nonce + ciphertext + tag
            aad: Associated Authenticated Data
            
        Returns:
            Decrypted plaintext
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if len(data) < 28:  # minimum: 12 nonce + 0 ciphertext + 16 tag
            raise ValueError("Data too short for GCM")
        
        # Parse input
        nonce = data[:12]
        tag = data[-16:]
        ciphertext = data[12:-16]
        
        # Reconstruct J0 from nonce
        if len(nonce) == 12:
            j0 = nonce + b'\x00\x00\x00\x01'
        else:
            # For non-12-byte nonce (simplified)
            s = 16 * ((len(nonce) + 15) // 16) - len(nonce)
            padded_nonce = nonce + bytes(s)
            len_nonce = (len(nonce) * 8).to_bytes(16, 'big')
            j0 = self._ghash(padded_nonce + len_nonce, b"")
        
        # Verify authentication tag
        s = self._ghash(aad, ciphertext)
        computed_tag = self._gctr(j0, s)
        
        if computed_tag != tag:
            raise AuthenticationError("Authentication failed: AAD mismatch or ciphertext tampered")
        
        # Decrypt ciphertext
        icb = j0
        plaintext = self._gctr(icb, ciphertext)
        
        return plaintext
