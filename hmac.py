import os
from src.hash.sha256 import SHA256

class HMAC:
    def __init__(self, key, hash_function='sha256'):
       
        if isinstance(key, str):
            # Если ключ передан как шестнадцатеричная строка
            self.key = bytes.fromhex(key)
        elif isinstance(key, bytes):
            self.key = key
        else:
            raise ValueError("Key must be bytes or hex string")
        
        self.hash_function_name = hash_function.lower()
        
        if self.hash_function_name == 'sha256':
            self.hash_function = SHA256
            self.block_size = 64  # bytes для SHA-256
            self.output_size = 32  # bytes для SHA-256
        else:
            raise ValueError(f"Unsupported hash function: {hash_function}")
        
        # Обработка ключа согласно RFC 2104
        self.key = self._process_key(self.key)
    
    def _process_key(self, key):
       
        # Если ключ длиннее размера блока, хэшируем его
        if len(key) > self.block_size:
            hash_obj = self.hash_function()
            hash_obj.update(key)
            key = hash_obj.digest()
        
        # Если ключ короче размера блока, дополняем нулями
        if len(key) < self.block_size:
            key = key + b'\x00' * (self.block_size - len(key))
        
        return key
    
    def _xor_bytes(self, a, b):
       
        return bytes(x ^ y for x, y in zip(a, b))
    
    def compute(self, message):
      
        # Создаем внутренний и внешний пады
        ipad = self._xor_bytes(self.key, b'\x36' * self.block_size)
        opad = self._xor_bytes(self.key, b'\x5c' * self.block_size)
        
        # Внутренний хэш: H((K ⊕ ipad) ∥ message)
        inner_hash = self.hash_function()
        inner_hash.update(ipad + message)
        inner_hash_result = inner_hash.digest()
        
        # Внешний хэш: H((K ⊕ opad) ∥ inner_hash)
        outer_hash = self.hash_function()
        outer_hash.update(opad + inner_hash_result)
        outer_hash_result = outer_hash.digest()
        
        return outer_hash_result.hex()
    
    def compute_file(self, filepath, chunk_size=4096):
     
        # Создаем внутренний и внешний пады
        ipad = self._xor_bytes(self.key, b'\x36' * self.block_size)
        opad = self._xor_bytes(self.key, b'\x5c' * self.block_size)
        
        # Внутренний хэш: H((K ⊕ ipad) ∥ message)
        inner_hash = self.hash_function()
        inner_hash.update(ipad)
        
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                inner_hash.update(chunk)
        
        inner_hash_result = inner_hash.digest()
        
        # Внешний хэш: H((K ⊕ opad) ∥ inner_hash)
        outer_hash = self.hash_function()
        outer_hash.update(opad + inner_hash_result)
        outer_hash_result = outer_hash.digest()
        
        return outer_hash_result.hex()
