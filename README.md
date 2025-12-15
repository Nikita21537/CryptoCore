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

# Шифрование с автоматической генерацией ключа
python src/main.py --algorithm aes --mode ctr --encrypt --input plaintext.txt --output ciphertext.bin
[INFO] Generated random key: 1a2b3c4d5e6f7890fedcba9876543210
# Дешифрование (ключ обязателен)
python src/main.py --algorithm aes --mode ctr --decrypt --key 1a2b3c4d5e6f7890fedcba9876543210 --input ciphertext.bin --output decrypted.txt
Тестирование NIST STS
Для запуска тестов NIST Statistical Test Suite:
#Сгенерируйте тестовые данные:

python tests/test_csprng.py
#Скачайте и установите NIST STS

#Запустите тесты:
# Сгенерируйте файл для тестирования
python -c "from src.csprng import generate_random_bytes; data = generate_random_bytes(10000000); open('random_test_data.bin', 'wb').write(data)"

# Запустите NIST STS
assess 10000000
## Спринт 4: Хеш-функции для проверки целостности данных

### Новые команды

Инструмент теперь поддерживает subcommand `dgst` для вычисления хешей:


# Базовое вычисление хеша
python src/main.py dgst --algorithm sha256 --input document.pdf
5d5b09f6dcb2d53a5fffc60c4ac0d55fb052072fa2fe5d95f011b5d5d5b0b0b5  document.pdf

# Хеш с выводом в файл
python src/main.py dgst --algorithm sha3-256 --input backup.tar --output backup.sha3

# Хеш из stdin
echo -n "hello" | python src/main.py dgst --algorithm sha256 --input -
# Новый синтаксис с subcommand 'enc'
python src/main.py enc --algorithm aes --mode cbc --encrypt --input plain.txt --output cipher.bin

# Старый синтаксис все еще поддерживается для обратной совместимости
python src/main.py --algorithm aes --mode cbc --encrypt --input plain.txt --output cipher.bin
# Запустите тесты хеш-функций
python tests/test_hash.py

# Проверка известных тестовых векторов
echo -n "abc" | python src/main.py dgst --algorithm sha256 --input -
# Должно вывести: ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
### Добавлено
- Реализация SHA3 с нуля (from scratch)
- Реализация BLAKE2b с поддержкой различных размеров
- Подробные тесты для новых алгоритмов
- Документация и примеры использования
# HMAC (Hash-based Message Authentication Code)

## Описание
HMAC - это механизм для проверки целостности и подлинности сообщений с использованием криптографических хэш-функций.

## Использование

### Генерация HMAC

cryptocore dgst --algorithm sha256 --hmac --key <ключ> --input <файл>  
пример
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.txt
### Верефикация HMAC
cryptocore dgst --algorithm sha256 --hmac --key <ключ> --input <файл> --verify <файл_с_hmac>
пример
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.txt --verify expected_hmac.txt
### Параметры
--hmac: Включить режим HMAC
--key KEY: Ключ для HMAC (шестнадцатеричная строка)
--verify FILE: Файл с ожидаемым значением HMAC для верификации
### Формат вывода
При генерации HMAC вывод имеет формат:
HMAC_VALUE INPUT_FILE_PATH
Пример
a1b2c3d4e5f6012345678901234567890123456789012345678901234567890123 message.txt

### Тестовые векторы
RFC 4231 Test Case 1
echo -n "Hi There" > test.txt
cryptocore dgst --algorithm sha256 --hmac --key 0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b --input test.txt
Ожидаемый результат: b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7
### Безопасность
HMAC обеспечивает:
Целостность данных
Аутентификацию источника
Защиту от подделки
Ключевые свойства:
Использует SHA-256 в качестве базовой хэш-функции
Поддерживает ключи произвольной длины
Устойчив к атакам на удлинение сообщений
