import os
import pytest
import struct
from src.modes.gcm import GCM, AuthenticationError

def test_gcm_encrypt_decrypt():
  
    key = os.urandom(16)
    plaintext = b"Hello, GCM world!"
    aad = b"associated_data"
    

    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, aad)
    
    
    gcm2 = GCM(key, gcm.nonce)
    decrypted = gcm2.decrypt(ciphertext, aad)
    
    assert decrypted == plaintext
    assert len(ciphertext) == len(plaintext) + 12 + 16  # + nonce + tag

def test_gcm_aad_tamper():
    
    key = os.urandom(16)
    plaintext = b"Secret message"
    aad_correct = b"correct_aad"
    aad_wrong = b"wrong_aad"
    
   
    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, aad_correct)
    
  
    gcm2 = GCM(key, gcm.nonce)
    
    with pytest.raises(AuthenticationError):
        gcm2.decrypt(ciphertext, aad_wrong)

def test_gcm_ciphertext_tamper():

    key = os.urandom(16)
    plaintext = b"Another secret message"
    aad = b"associated_data"
    
    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, aad)
    
    tampered = bytearray(ciphertext)
    tampered[20] ^= 0x01  # Flip a bit in the ciphertext part
    
 
    gcm2 = GCM(key, gcm.nonce)
    
    with pytest.raises(AuthenticationError):
        gcm2.decrypt(bytes(tampered), aad)

def test_gcm_nonce_uniqueness():
    
    key = os.urandom(16)
    plaintext = b"Test message"
    
    nonces = set()
    for _ in range(100):
        gcm = GCM(key)
        nonces.add(gcm.nonce)
    
    assert len(nonces) == 100, "Nonces should be unique"

def test_gcm_empty_aad():
    
    key = os.urandom(16)
    plaintext = b"Message with empty AAD"
    
    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, b"")
    
    gcm2 = GCM(key, gcm.nonce)
    decrypted = gcm2.decrypt(ciphertext, b"")
    
    assert decrypted == plaintext

def test_gcm_large_data():
  
    key = os.urandom(16)
    plaintext = os.urandom(1024 * 1024)  # 1MB
    aad = os.urandom(512)  # 512 bytes AAD
    
    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, aad)
    
    gcm2 = GCM(key, gcm.nonce)
    decrypted = gcm2.decrypt(ciphertext, aad)
    
    assert decrypted == plaintext

def test_gcm_nist_test_vector():
    
    # Simple test vector (not from NIST, but for basic verification)
    key = bytes.fromhex('00000000000000000000000000000000')
    nonce = bytes.fromhex('000000000000000000000000')
    plaintext = b""
    aad = b""
    
    gcm = GCM(key, nonce)
    ciphertext = gcm.encrypt(plaintext, aad)
    
    # For empty input, we should still get nonce + tag
    assert len(ciphertext) == 12 + 0 + 16
    assert ciphertext[:12] == nonce

def test_gcm_tag_tamper():
    
    key = os.urandom(16)
    plaintext = b"Message to tamper with"
    aad = b"aad"
    
    gcm = GCM(key)
    ciphertext = gcm.encrypt(plaintext, aad)
    
 
    tampered = bytearray(ciphertext)
    tampered[-1] ^= 0x01  # Flip last bit of tag
    
    gcm2 = GCM(key, gcm.nonce)
    
    with pytest.raises(AuthenticationError):
        gcm2.decrypt(bytes(tampered), aad)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
