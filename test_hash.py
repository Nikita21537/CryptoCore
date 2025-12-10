import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from hash import SHA3_256, BLAKE2b, sha3_256, blake2b
from src.hash import get_hash_algorithm

def test_sha256_known_answers():
   
    # Test vectors from NIST
    test_vectors = [
        ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        ("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", 
         "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    ]
    
    sha256 = get_hash_algorithm('sha256')
    
    for message, expected in test_vectors:
        result = sha256.hash(message.encode('utf-8'))
        assert result == expected, f"SHA-256 failed for '{message}': got {result}, expected {expected}"
    
    print(" SHA-256 known answer tests passed")

def test_sha3_256_known_answers():
    
    # Basic test vectors
    test_vectors = [
        ("", "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
        ("abc", "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"),
    ]
    
    sha3_256 = get_hash_algorithm('sha3-256')
    
    for message, expected in test_vectors:
        result = sha3_256.hash(message.encode('utf-8'))
        assert result == expected, f"SHA3-256 failed for '{message}': got {result}, expected {expected}"
    
    print(" SHA3-256 known answer tests passed")

def test_avalanche_effect():
    
    original_data = b"Hello, world!"
    modified_data = b"Hello, world?"  
    
    sha256 = get_hash_algorithm('sha256')
    hash1 = sha256.hash(original_data)
    
    sha256 = get_hash_algorithm('sha256')  
    hash2 = sha256.hash(modified_data)
    
    
    bin1 = bin(int(hash1, 16))[2:].zfill(256)
    bin2 = bin(int(hash2, 16))[2:].zfill(256)
    
    diff_count = sum(bit1 != bit2 for bit1, bit2 in zip(bin1, bin2))
    print(f"✓ Bits changed: {diff_count}/256")
    
    
    assert 100 < diff_count < 156, f"Avalanche effect weak: only {diff_count} bits changed"
    print("✓ Avalanche effect test passed")

def test_large_file_simulation():
    
    
    large_data = b"X" * (1024 * 1024)  
    
    sha256 = get_hash_algorithm('sha256')
    
    
    chunk_size = 8192
    for i in range(0, len(large_data), chunk_size):
        chunk = large_data[i:i + chunk_size]
        sha256.update(chunk)
    
    result = sha256.hexdigest()
    
   
    sha256_one_shot = get_hash_algorithm('sha256')
    expected = sha256_one_shot.hash(large_data)
    
    assert result == expected, 
    print(" Large file chunk processing test passed")

def test_interoperability():
    
    test_data = b"Test data for interoperability check"
    

    for algo in ['sha256', 'sha3-256']:
        hash_obj = get_hash_algorithm(algo)
        result = hash_obj.hash(test_data)
        
        
        assert len(result) == 64, f"{algo} hash length incorrect: {len(result)}"
        assert all(c in '0123456789abcdef' for c in result), f"{algo} hash contains invalid characters"
        
        print(f" {algo} interoperability format check passed")
# Тест SHA3-256
print("=== SHA3-256 Tests ===")
data = b"hello world"

# Способ 1: через класс
hasher1 = SHA3_256()
hasher1.update(data)
print(f"SHA3-256: {hasher1.hexdigest()}")

# Способ 2: через функцию
hasher2 = sha3_256(data)
print(f"SHA3-256: {hasher2.hexdigest()}")

print("\n=== BLAKE2b Tests ===")
# BLAKE2b-512 (по умолчанию)
hasher3 = BLAKE2b()
hasher3.update(data)
print(f"BLAKE2b-512: {hasher3.hexdigest()}")

# BLAKE2b-256
hasher4 = BLAKE2b(digest_size=32)
hasher4.update(data)
print(f"BLAKE2b-256: {hasher4.hexdigest()}")

# Через функцию
hasher5 = blake2b(data, digest_size=32)
print(f"BLAKE2b-256: {hasher5.hexdigest()}")

if __name__ == "__main__":
    print("Running hash function tests...")
    
    test_sha256_known_answers()
    test_sha3_256_known_answers()
    test_avalanche_effect()
    test_large_file_simulation()
    test_interoperability()
    
    print(" All hash tests passed!")
