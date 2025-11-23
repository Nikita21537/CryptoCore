#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.csprng import generate_random_bytes, is_weak_key

def test_key_uniqueness():
    """Test that generated keys are unique"""
    key_set = set()
    num_keys = 1000
    
    for _ in range(num_keys):
        key = generate_random_bytes(16)
        key_hex = key.hex()
        
        # Check for uniqueness
        assert key_hex not in key_set, f"Duplicate key found: {key_hex}"
        key_set.add(key_hex)
    
    print(f"✓ Successfully generated {len(key_set)} unique keys.")

def test_weak_key_detection():
   
    # Test all zeros
    zero_key = bytes(16)
    assert is_weak_key(zero_key) == True, "All zeros key should be detected as weak"
    
    # Test sequential increasing
    sequential_inc = bytes(range(16))
    assert is_weak_key(sequential_inc) == True, "Sequential increasing key should be detected as weak"
    
    # Test sequential decreasing
    sequential_dec = bytes(range(15, -1, -1))
    assert is_weak_key(sequential_dec) == True, "Sequential decreasing key should be detected as weak"
    
    # Test repeating pattern
    repeating = b'\x01\x02\x01\x02' * 4
    assert is_weak_key(repeating) == True, "Repeating pattern key should be detected as weak"
    
    # Test strong key (should not be detected as weak)
    strong_key = generate_random_bytes(16)
    assert is_weak_key(strong_key) == False, "Random key should not be detected as weak"
    
    print("✓ Weak key detection working correctly")

def test_basic_entropy():
    """Test basic entropy properties of generated keys"""
    num_keys = 100
    total_bits = 0
    total_set_bits = 0
    
    for _ in range(num_keys):
        key = generate_random_bytes(16)
        # Count set bits (1s)
        for byte in key:
            total_bits += 8
            total_set_bits += bin(byte).count('1')
    
    set_bit_ratio = total_set_bits / total_bits
    print(f"✓ Set bit ratio: {set_bit_ratio:.3f} (expected ~0.5)")
    
    # Check if ratio is close to 0.5 (good entropy)
    assert 0.4 <= set_bit_ratio <= 0.6, f"Bit ratio {set_bit_ratio} outside expected range"

def test_nist_preparation():
    """Generate a large random file for NIST testing"""
    total_size = 10_000_000  # 10 MB
    
    with open('nist_test_data.bin', 'wb') as f:
        bytes_written = 0
        while bytes_written < total_size:
            chunk_size = min(4096, total_size - bytes_written)
            random_chunk = generate_random_bytes(chunk_size)
            f.write(random_chunk)
            bytes_written += chunk_size
    
    print(f" Generated {bytes_written} bytes for NIST testing in 'nist_test_data.bin'")

def test_error_handling():
    
    try:
        generate_random_bytes(0)
        assert False, "Should have raised ValueError for 0 bytes"
    except ValueError:
        pass
    
    try:
        generate_random_bytes(-1)
        assert False, "Should have raised ValueError for negative bytes"
    except ValueError:
        pass
    
    print("✓ Error handling working correctly")

if __name__ == "__main__":
    print("Running CSPRNG tests...")
    
    test_key_uniqueness()
    test_weak_key_detection()
    test_basic_entropy()
    test_error_handling()
    
    # Uncomment to generate NIST test data
    # test_nist_preparation()
    
    print(" All CSPRNG tests passed!")
