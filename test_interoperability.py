#!/usr/bin/env python3
import os
import subprocess
import tempfile

def run_command(cmd):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_mode(mode, key, iv=None):
    """Тестирует конкретный режим на совместимость с OpenSSL"""
    print(f"\n=== Testing {mode.upper()} mode ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        # Создаем тестовый файл
        test_content = "Hello, CryptoCore! This is a test message for interoperability testing."
        f.write(test_content)
        plaintext_file = f.name
    
    try:
        # 1. Шифрование нашим инструментом
        cipher_file = f"test_{mode}.bin"
        decrypt_file = f"test_{mode}_decrypted.txt"
        
        # Шифрование
        encrypt_cmd = f"python src/main.py --algorithm aes --mode {mode} --encrypt --key {key} --input {plaintext_file} --output {cipher_file}"
        success, stdout, stderr = run_command(encrypt_cmd)
        if not success:
            print(f"Encryption failed: {stderr}")
            return False
        
        # 2. Дешифрование OpenSSL
        # Извлекаем IV из файла
        iv_extract_cmd = f"dd if={cipher_file} of=iv.bin bs=16 count=1 2>/dev/null"
        run_command(iv_extract_cmd)
        
        cipher_only_cmd = f"dd if={cipher_file} of=cipher_only.bin bs=16 skip=1 2>/dev/null"
        run_command(cipher_only_cmd)
        
        # Получаем IV в hex
        with open('iv.bin', 'rb') as f:
            iv_hex = f.read().hex()
        
        # Дешифрование OpenSSL
        openssl_decrypt_cmd = f"openssl enc -aes-128-{mode} -d -K {key} -iv {iv_hex} -in cipher_only.bin -out openssl_decrypted.txt"
        success, stdout, stderr = run_command(openssl_decrypt_cmd)
        if not success:
            print(f"OpenSSL decryption failed: {stderr}")
            return False
        
        # Проверяем результат
        with open(plaintext_file, 'r') as f:
            original = f.read()
        with open('openssl_decrypted.txt', 'r') as f:
            decrypted = f.read()
        
        if original == decrypted:
            print("✓ Our tool -> OpenSSL: SUCCESS")
        else:
            print("✗ Our tool -> OpenSSL: FAILED")
            return False
        
        # 3. Шифрование OpenSSL, дешифрование нашим инструментом
        if iv is None:
            iv = 'AABBCCDDEEFF00112233445566778899'
        
        openssl_encrypt_cmd = f"openssl enc -aes-128-{mode} -K {key} -iv {iv} -in {plaintext_file} -out openssl_cipher.bin"
        success, stdout, stderr = run_command(openssl_encrypt_cmd)
        if not success:
            print(f"OpenSSL encryption failed: {stderr}")
            return False
        
        # Дешифрование нашим инструментом
        our_decrypt_cmd = f"python src/main.py --algorithm aes --mode {mode} --decrypt --key {key} --iv {iv} --input openssl_cipher.bin --output {decrypt_file}"
        success, stdout, stderr = run_command(our_decrypt_cmd)
        if not success:
            print(f"Our tool decryption failed: {stderr}")
            return False
        
        # Проверяем результат
        with open(decrypt_file, 'r') as f:
            our_decrypted = f.read()
        
        if original == our_decrypted:
            print("✓ OpenSSL -> Our tool: SUCCESS")
            return True
        else:
            print("✗ OpenSSL -> Our tool: FAILED")
            return False
            
    finally:
        # Очистка
        for file in [plaintext_file, cipher_file, decrypt_file, 'iv.bin', 'cipher_only.bin', 'openssl_decrypted.txt', 'openssl_cipher.bin']:
            if os.path.exists(file):
                os.remove(file)

def main():
    key = "000102030405060708090a0b0c0d0e0f"
    
    modes = ['cbc', 'cfb', 'ofb', 'ctr']
    
    all_passed = True
    for mode in modes:
        if not test_mode(mode, key):
            all_passed = False
    
    print(f"\n=== Overall Result ===")
    if all_passed:
        print("✓ All interoperability tests PASSED")
    else:
        print("✗ Some tests FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
