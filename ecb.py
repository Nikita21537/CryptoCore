from Crypto.Cipher import AES
import sys

def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    """
    Дополнение данных по стандарту PKCS#7
    """
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding

def pkcs7_unpad(data: bytes) -> bytes:
    """
    Удаление дополнения PKCS#7
    """
    if len(data) == 0:
        return data
    
    padding_length = data[-1]
    
    # Проверка валидности дополнения
    if padding_length > len(data) or padding_length == 0:
        raise ValueError("Неверное дополнение PKCS#7")
    
    if data[-padding_length:] != bytes([padding_length] * padding_length):
        raise ValueError("Неверное дополнение PKCS#7")
    
    return data[:-padding_length]

def encrypt_ecb(plaintext: bytes, key: bytes) -> bytes:
    """
    Шифрование в режиме ECB
    """
    # Дополнение данных
    padded_data = pkcs7_pad(plaintext)
    
    # Создание cipher объекта
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Шифрование по блокам
    ciphertext = b''
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        encrypted_block = cipher.encrypt(block)
        ciphertext += encrypted_block
    
    return ciphertext

def decrypt_ecb(ciphertext: bytes, key: bytes) -> bytes:
    """
    Дешифрование в режиме ECB
    """
    # Проверка что размер шифртекста кратен 16 байтам
    if len(ciphertext) % 16 != 0:
        raise ValueError("Размер шифртекста должен быть кратен 16 байтам")
    
    # Создание cipher объекта
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Дешифрование по блокам
    decrypted_data = b''
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        decrypted_block = cipher.decrypt(block)
        decrypted_data += decrypted_block
    
    # Удаление дополнения
    return pkcs7_unpad(decrypted_data)
