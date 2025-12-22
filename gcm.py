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
            
        
        self.H = self._aes_encrypt_block(bytes(16))
        
       
        self._precompute_mul_table()
        
    def _aes_encrypt_block(self, block: bytes) -> bytes:
       
        return self.aes.encrypt(block)
    
    def _precompute_mul_table(self):
      
        self.M = [0] * 16
        self.M[0] = 0
        
   
        self.M[1] = int.from_bytes(self.H, 'big')
        

        for i in range(2, 16):
            self.M[i] = self._mult_gf2_128(self.M[i-1], self.M[1])
    
    def _mult_gf2_128(self, x: int, y: int) -> int:
     
        z = 0
        v = y
        
      
        poly = 0xE1000000000000000000000000000000
        
        for i in range(127, -1, -1):
            if (x >> i) & 1:
                z ^= v
         
            if v & 1:
                v = (v >> 1) ^ poly
            else:
                v >>= 1
        return z
    
    def _ghash(self, aad: bytes, ciphertext: bytes) -> bytes:
       
       
        len_aad = len(aad) * 8  # bits
        len_c = len(ciphertext) * 8  # bits
        
      
        len_block = struct.pack('>QQ', len_aad, len_c)
        
      
        y = 0
        pos = 0
        
       
        while pos < len(aad):
            block = aad[pos:pos+16]
            if len(block) < 16:
                block = block + bytes(16 - len(block))
            block_int = int.from_bytes(block, 'big')
            y ^= block_int
            y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
            pos += 16
        
       
        pos = 0
        while pos < len(ciphertext):
            block = ciphertext[pos:pos+16]
            if len(block) < 16:
                block = block + bytes(16 - len(block))
            block_int = int.from_bytes(block, 'big')
            y ^= block_int
            y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
            pos += 16
        
        
        len_int = int.from_bytes(len_block, 'big')
        y ^= len_int
        y = self._mult_gf2_128(y, int.from_bytes(self.H, 'big'))
        
        return y.to_bytes(16, 'big')
    
    def _gctr(self, icb: bytes, x: bytes) -> bytes:
      
        if not x:
            return b''
        
        n = (len(x) + 15) // 16  # Number of 16-byte blocks
        y = b''
        cb = icb
        
        for i in range(n):
           
            encrypted_cb = self._aes_encrypt_block(cb)
            
           
            start = i * 16
            end = min((i + 1) * 16, len(x))
            block = x[start:end]
            
      
            if len(block) < 16:
                encrypted_cb = encrypted_cb[:len(block)]
            y_block = bytes(a ^ b for a, b in zip(block, encrypted_cb))
            y += y_block
            
         
            if len(cb) == 16:
                counter = int.from_bytes(cb[12:], 'big')
                counter = (counter + 1) & 0xFFFFFFFF
                cb = cb[:12] + counter.to_bytes(4, 'big')
        
        return y
    
    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        
        
        if len(self.nonce) == 12:
            j0 = self.nonce + b'\x00\x00\x00\x01'
        else:
   
            s = 16 * ((len(self.nonce) + 15) // 16) - len(self.nonce)
            padded_nonce = self.nonce + bytes(s)
            len_nonce = (len(self.nonce) * 8).to_bytes(16, 'big')
            j0 = self._ghash(padded_nonce + len_nonce, b"")
       
        icb = j0
        
  
        ciphertext = self._gctr(icb, plaintext)
        
       
        s = self._ghash(aad, ciphertext)
        t = self._gctr(j0, s)
        
        return self.nonce + ciphertext + t
    
    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:
      
        if len(data) < 28: 
            raise ValueError("Data too short for GCM")
        
  
        nonce = data[:12]
        tag = data[-16:]
        ciphertext = data[12:-16]
        
 
        if len(nonce) == 12:
            j0 = nonce + b'\x00\x00\x00\x01'
        else:
           
            s = 16 * ((len(nonce) + 15) // 16) - len(nonce)
            padded_nonce = nonce + bytes(s)
            len_nonce = (len(nonce) * 8).to_bytes(16, 'big')
            j0 = self._ghash(padded_nonce + len_nonce, b"")
        
      
        s = self._ghash(aad, ciphertext)
        computed_tag = self._gctr(j0, s)
        
        if computed_tag != tag:
            raise AuthenticationError("Authentication failed: AAD mismatch or ciphertext tampered")
        
   
        icb = j0
        plaintext = self._gctr(icb, ciphertext)
        
        return plaintext
