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
### Поддерживаемые режимы
- `cbc` - Cipher Block Chaining
- `cfb` - Cipher Feedback  
- `ofb` - Output Feedback
- `ctr` - Counter

### Использование с новыми режимами

#### Шифрование (IV генерируется автоматически)
```bash
python src/main.py --algorithm aes --mode cbc --encrypt \
    --key 000102030405060708090a0b0c0d0e0f \
    --input plaintext.txt --output ciphertext.bin
python src/main.py --algorithm aes --mode cbc --decrypt \
    --key 000102030405060708090a0b0c0d0e0f \
    --iv aabbccddeeff00112233445566778899 \
    --input ciphertext.bin --output decrypted.txt
###Дешифрование (IV читается из файла)
python src/main.py --algorithm aes --mode cbc --decrypt \
    --key 000102030405060708090a0b0c0d0e0f \
    --input ciphertext.bin --output decrypted.txt
# Шифрование
python src/main.py --algorithm aes --mode cbc --encrypt \
    --key 000102030405060708090a0b0c0d0e0f \
    --input plain.txt --output cipher.bin

# Извлечение IV и шифротекста
dd if=cipher.bin of=iv.bin bs=16 count=1
dd if=cipher.bin of=ciphertext_only.bin bs=16 skip=1

# Дешифрование OpenSSL
openssl enc -aes-128-cbc -d \
    -K 000102030405060708090a0b0c0d0e0f \
    -iv $(xxd -p iv.bin | tr -d '\n') \
    -in ciphertext_only.bin -out decrypted.txt
# Шифрование OpenSSL
openssl enc -aes-128-cbc \
    -K 000102030405060708090a0b0c0d0e0f \
    -iv AABBCCDDEEFF00112233445566778899 \
    -in plain.txt -out openssl_cipher.bin

# Дешифрование
python src/main.py --algorithm aes --mode cbc --decrypt \
    --key 000102030405060708090a0b0c0d0e0f \
    --iv AABBCCDDEEFF00112233445566778899 \
    --input openssl_cipher.bin --output decrypted.txt

## Спринт 3: Безопасный источник случайности

### Автоматическая генерация ключей

Теперь инструмент поддерживает автоматическую генерацию криптографически стойких ключей:

```bash
# Шифрование с автоматической генерацией ключа
python src/main.py --algorithm aes --mode ctr --encrypt --input plaintext.txt --output ciphertext.bin
[INFO] Generated random key: 1a2b3c4d5e6f7890fedcba9876543210

# Дешифрование (ключ обязателен)
python src/main.py --algorithm aes --mode ctr --decrypt --key 1a2b3c4d5e6f7890fedcba9876543210 --input ciphertext.bin --output decrypted.txt
Тестирование NIST STS
Для запуска тестов NIST Statistical Test Suite:

Сгенерируйте тестовые данные:


python tests/test_csprng.py
Скачайте и установите NIST STS

Запустите тесты:


# Сгенерируйте файл для тестирования
python -c "from src.csprng import generate_random_bytes; data = generate_random_bytes(10000000); open('random_test_data.bin', 'wb').write(data)"

# Запустите NIST STS
./assess 10000000
