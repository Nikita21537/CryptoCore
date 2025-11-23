import os
import sys

def generate_random_bytes(num_bytes):
  
    if num_bytes <= 0:
        raise ValueError("Number of bytes must be positive")
    
    try:
        return os.urandom(num_bytes)
    except Exception as e:
        raise RuntimeError(f"Failed to generate random bytes: {e}")

def is_weak_key(key_bytes):
   
    if not key_bytes:
        return False
    

    if all(byte == 0 for byte in key_bytes):
        return True
    
   
    is_sequential_inc = all(key_bytes[i] == (key_bytes[i-1] + 1) % 256 
                           for i in range(1, len(key_bytes)))
    is_sequential_dec = all(key_bytes[i] == (key_bytes[i-1] - 1) % 256 
                           for i in range(1, len(key_bytes)))
    
    if is_sequential_inc or is_sequential_dec:
        return True
    
    
    if len(key_bytes) >= 4:
        # Check if key is all the same byte
        if all(byte == key_bytes[0] for byte in key_bytes):
            return True
        
        
        for pattern_len in [2, 4]:
            if len(key_bytes) % pattern_len == 0:
                pattern = key_bytes[:pattern_len]
                repeats_correctly = all(key_bytes[i:i+pattern_len] == pattern 
                                      for i in range(pattern_len, len(key_bytes), pattern_len))
                if repeats_correctly:
                    return True
    
    return False
