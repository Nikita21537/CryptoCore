# CryptoCore

Проект CryptoCore - это инструмент командной строки для криптографических операций с использованием блочных шифров.

## Зависимости

- Python 3.6+
- pycryptodome

## Установка


pip install -r requirements.txt
# шифрование
python cryptocore.py --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
# Дешифрование
python cryptocore.py --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
# Тестирование 
# Создаем тестовый файл
echo "Hello, CryptoCore!" > test_input.txt

# Шифруем
python cryptocore.py --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input test_input.txt --output test_encrypted.bin

# Дешифруем
python cryptocore.py --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input test_encrypted.bin --output test_decrypted.txt

# Проверяем результат
diff test_input.txt test_decrypted.txt
