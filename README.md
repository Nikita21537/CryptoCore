## CryptoCore - AES-128 ECB Инструмент Шифрования/Расшифровки
# Инструмент командной строки для режима AES-128 ECB шифрования и расшифровки с PKCS#7 дополнением.




## Инструкции по сборке
sudo apt install git

sudo apt update

sudo apt install python3-venv python3-pip python3-full

git clone https://github.com/kdqwrt/cryptocore.git

python3 -m venv venv

source venv/bin/activate

cd cryptocore

dir 

pip install --upgrade pip

pip install -e .

pip install setuptools wheel

python all_tests.py
## Команды
echo "Тестовые данные" > test.txt

cryptocore encrypt --mode gcm --encrypt --input test.txt --output test.enc
cryptocore encrypt --mode gcm --decrypt --key @ВАШ_КЛЮЧ --input test.enc --output test_decrypted.txt
cat test_decrypted.txt
## Основные команды
## Шифрование GCM

cryptocore encrypt --mode gcm --encrypt --key @00112233445566778899aabbccddeeff --input файл.txt --output файл.enc
cryptocore encrypt --mode gcm --decrypt --key @00112233445566778899aabbccddeeff --input файл.enc --output файл.txt
## Шифрование GCM с AAD

cryptocore encrypt --mode gcm --encrypt --key @ключ --input данные.txt --output данные.enc --aad 0102030405
cryptocore encrypt --mode gcm --decrypt --key @ключ --input данные.enc --output данные.txt --aad 0102030405
## Другие режимы шифрования

cryptocore encrypt --mode cbc --encrypt --key @ключ --input файл.txt --output файл.enc
cryptocore encrypt --mode ctr --encrypt --key @ключ --input файл.txt --output файл.enc
cryptocore encrypt --mode ecb --encrypt --key @ключ --input файл.txt --output файл.enc
## Хеширование файлов

cryptocore dgst --algorithm sha256 --input файл.iso
cryptocore dgst --algorithm sha3-256 --input файл.iso
cryptocore dgst --algorithm sha256 --input файл1.txt файл2.txt файл3.txt
## HMAC подписи

cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input файл.txt
cryptocore dgst --algorithm sha256 --hmac --key ключ --input файл.txt --verify файл.hmac
## Работа с ключами

python3 -c "import os; print('@' + os.urandom(16).hex())"
cryptocore derive --password "пароль" --salt a1b2c3d4e5f6 --iterations 100000 --length 16



# Инструкции по сборке
Используя pip:
pip install -e .

# Ручная установка:
pip install -r requirements.txt

# Инструкции по использованию
Шифрование:
cryptocore --algorithm aes --mode ecb --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input plaintext.txt
--output ciphertext.bin

# Расшифровка:
cryptocore --algorithm aes --mode ecb --decrypt
--key 000102030405060708090a0b0c0d0e0f
--input ciphertext.bin
--output decrypted.txt

# Зависимости
Python 3.6 или выше

библиотека pycryptodome (pip install pycryptodome)

#Структура проектаcryptocore.py
csprng.py
file_io.py
cli_parser.py
cryptocore/
├── src/
│ ├── cli_parser.py
│ ├── file_io.py
│ ├── modes/
│ │ └── ecb.py
│ └── cryptocore.py
├── tests/
├── requirements.txt
├── setup.py
└── README.md

# Тестирование
Запустите набор тестов:
make test

# Или напрямую:
python -m pytest tests/

# Тест на полный цикл:
Создайте тестовый файл
echo "Hello, CryptoCore!" > test.txt

# Зашифруйте его
cryptocore --algorithm aes --mode ecb --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input test.txt
--output test.enc

# Расшифруйте его
cryptocore --algorithm aes --mode ecb --decrypt
--key 000102030405060708090a0b0c0d0e0f
--input test.enc
--output test.dec

Проверьте
diff test.txt test.dec # Не должно быть различий

Проверка с помощью OpenSSL
Для проверки реализации в сравнении с OpenSSL:

# Зашифруйте с помощью CryptoCore
cryptocore --algorithm aes --mode ecb --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input plaintext.txt
--output cryptocore.bin

Зашифруйте с помощью OpenSSL (для файлов кратных 16 байтам)
openssl enc -aes-128-ecb
-K 000102030405060708090a0b0c0d0e0f
-in plaintext.txt
-out openssl.bin
-nopad

Сравните (для файлов кратных 16 байтам)
cmp cryptocore.bin openssl.bin

Примечание: OpenSSL с параметром -nopad работает только для файлов, размер которых кратен 16 байтам. CryptoCore автоматически обрабатывает PKCS#7 дополнение для файлов произвольной длины.



# 4. Инструкции по запуску
Создайте структуру проекта:

mkdir -p cryptocore/src/modes cryptocore/tests
Скопируйте все файлы в соответствующие директории

# Установите зависимости:
cd cryptocore
pip install -r requirements.txt

# Установите пакет:
pip install -e .

Протестируйте:
Тесты
python -m pytest tests/

Пример использования
echo "Hello, World!" > test.txt

cryptocore --algorithm aes --mode ecb --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input test.txt
--output test.enc

cryptocore --algorithm aes --mode ecb --decrypt
--key 000102030405060708090a0b0c0d0e0f
--input test.enc
--output test.dec

diff test.txt test.dec # Должно быть пусто

CryptoCore - AES-128 Инструмент Шифрования/Расшифровки
Инструмент командной строки для AES-128 шифрования и расшифровки с поддержкой нескольких режимов:
ECB, CBC, CFB, OFB и CTR с PKCS#7 дополнением, где это требуется.

# Инструкции по сборке
Используя pip:
pip install -e .

Ручная установка:
pip install -r requirements.txt

# Инструкции по использованию
Для режимов, требующих IV (CBC, CFB, OFB, CTR):
Шифрование (IV генерируется автоматически):
cryptocore --algorithm aes --mode cbc --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input plaintext.txt
--output ciphertext.bin

# Сгенерированный IV автоматически добавляется в начало файла с шифртекстом.

Расшифровка с явным указанием IV:
cryptocore --algorithm aes --mode cbc --decrypt
--key 000102030405060708090a0b0c0d0e0f
--iv AABBCCDDEEFF00112233445566778899
--input ciphertext.bin
--output decrypted.txt

# Расшифровка без явного указания IV (IV читается из файла):
cryptocore --algorithm aes --mode cbc --decrypt
--key 000102030405060708090a0b0c0d0e0f
--input ciphertext.bin
--output decrypted.txt

# Для режима ECB (без IV):
Шифрование:
cryptocore --algorithm aes --mode ecb --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input plaintext.txt
--output ciphertext.bin

Расшифровка:
cryptocore --algorithm aes --mode ecb --decrypt
--key 000102030405060708090a0b0c0d0e0f
--input ciphertext.bin
--output decrypted.txt

Зависимости
Python 3.6 или выше

библиотека pycryptodome (pip install pycryptodome)

# OpenSSL (для тестирования совместимости)

# Поддерживаемые режимы
ECB (Electronic Codebook) - Базовый режим, каждый блок шифруется независимо

CBC (Cipher Block Chaining) - Каждый блок XOR-ится с предыдущим шифртекстом

CFB (Cipher Feedback) - Режим потокового шифра, размер сегмента 128 бит

OFB (Output Feedback) - Режим потокового шифра, генерирует ключевой поток

CTR (Counter) - Режим потокового шифра с использованием счетчика

# Формат файла для режимов с IV
При шифровании в режимах CBC, CFB, OFB или CTR:
# Формат выходного файла: [16-байтовый IV][Байты шифртекста]
При расшифровке:
Если указан --iv: используется предоставленный IV

Если --iv не указан: читаются первые 16 байтов как IV из входного файла

Совместимость с OpenSSL
1. Зашифровать с помощью CryptoCore, расшифровать с помощью OpenSSL:
bash

# Зашифруйте с помощью CryptoCore
cryptocore --algorithm aes --mode cbc --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input plain.txt --output cipher.bin

# Извлеките IV и шифртекст
dd if=cipher.bin of=iv.bin bs=16 count=1
dd if=cipher.bin of=ciphertext_only.bin bs=16 skip=1

Расшифруйте с помощью OpenSSL
openssl enc -aes-128-cbc -d
-K 000102030405060708090A0B0C0D0E0F
-iv $(cat iv.bin | xxd -p | tr -d '\n')
-in ciphertext_only.bin
-out decrypted.txt

2. Зашифровать с помощью OpenSSL, расшифровать с помощью CryptoCore:
bash

Зашифруйте с помощью OpenSSL
openssl enc -aes-128-cbc
-K 000102030405060708090A0B0C0D0E0F
-iv AABBCCDDEEFF00112233445566778899
-in plain.txt -out openssl_cipher.bin

# Расшифруйте с помощью CryptoCore
cryptocore --algorithm aes --mode cbc --decrypt
--key 000102030405060708090a0b0c0d0e0f
--iv AABBCCDDEEFF00112233445566778899
--input openssl_cipher.bin
--output decrypted.txt

# Тестирование
Запустите набор тестов:

python -m pytest tests/

Или протестируйте определенные режимы:

Тест полного цикла CBC
python tests/test_modes.py TestNewModes.test_cbc_encrypt_decrypt

Тест совместимости с OpenSSL
python tests/test_modes.py TestNewModes.test_interoperability_openssl

# Структура проекта

##
cryptocore/
├── src/
│ ├── cli_parser.py
│ ├── file_io.py
│ ├── modes/
│ │ ├── base.py
│ │ ├── ecb.py
│ │ ├── cbc.py
│ │ ├── cfb.py
│ │ ├── ofb.py
│ │ └── ctr.py
│ └── cryptocore.py
├── tests/
├── requirements.txt
├── setup.py
└── README.md
##
Примечания
# Дополнение: Режимы ECB и CBC используют PKCS#7 дополнение. CFB, OFB и CTR являются потоковыми шифрами и не требуют дополнения.

 # Генерация IV: Для шифрования генерируется криптографически стойкий случайный IV с использованием os.urandom(16).

# Формат ключа: 16-байтовый ключ должен быть предоставлен в виде 32-символьной шестнадцатеричной строки.

# Формат IV: 16-байтовый IV должен быть предоставлен в виде 32-символьной шестнадцатеричной строки при указании.

# 4. Инструкции по установке и запуску
1. Активируйте виртуальное окружение
.\venv\Scripts\Activate.ps1

# 2. Установите зависимости
pip install pycryptodome

# 3. Установите пакет в development mode
pip install -e .

# 4. Тестирование
python -m pytest tests/test_modes.py -v

# 5. Пример использования всех режимов
Создайте тестовый файл
echo "Hello, this is a test file for all encryption modes!" > test.txt

# Тестируем каждый режим
$modes = @("ecb", "cbc", "cfb", "ofb", "ctr")
$key = "000102030405060708090a0b0c0d0e0f"

foreach ($mode in $modes) {
Write-Host "`nTesting $mode mode..." -ForegroundColor Green

Шифрование
cryptocore --algorithm aes --mode $mode --encrypt --key $key --input test.txt --output "test_$mode.enc"

Расшифровка
text
if ($mode -eq "ecb") {
    cryptocore --algorithm aes --mode $mode --decrypt --key $key --input "test_$mode.enc" --output "test_$mode.dec"
} else {
    # Для режимов с IV можно указать IV или читать из файла
    cryptocore --algorithm aes --mode $mode --decrypt --key $key --input "test_$mode.enc" --output "test_$mode.dec"
}
Проверка
diff test.txt "test_$mode.dec"

text
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ $mode mode works correctly!" -ForegroundColor Green
} else {
    Write-Host "  ✗ $mode mode failed!" -ForegroundColor Red
}
}

#  4. Обновленный
CryptoCore - AES-128 Инструмент Шифрования/Расшифровки
Инструмент командной строки для AES-128 шифрования и расшифровки с безопасной генерацией ключей,
поддерживающий режимы ECB, CBC, CFB, OFB и CTR.

# Возможности
Несколько режимов шифрования: ECB, CBC, CFB, OFB, CTR

Безопасная генерация ключей: Криптографически стойкая случайная генерация ключей

Автоматическая обработка IV: Безопасные случайные IV с правильным форматированием файлов

PKCS#7 дополнение: Для режимов, которые этого требуют (ECB, CBC)

Обнаружение слабых ключей: Предупреждает о потенциально небезопасных ключах

Совместимость: Совместим с OpenSSL для проверки

# Установка
Используя pip:
pip install -e .

 # Ручная установка:

pip install -r requirements.txt

# Быстрый старт
Шифрование с автоматической генерацией ключа


Ключ будет сгенерирован и отображен
cryptocore --algorithm aes --mode cbc --encrypt
--input secret.txt --output secret.enc

# Вывод будет включать:


[INFO] Сгенерированный ключ: 1a2b3c4d5e6f7890fedcba9876543210
[INFO] Статистика ключа: 64/128 бит установлены в 1 (50.0%)
[INFO] Пожалуйста, сохраните этот ключ для расшифровки!
[INFO] Сгенерированный IV (hex): aabbccddeeff00112233445566778899
[INFO] IV был записан в начало выходного файла.
Успешно зашифрован secret.txt -> secret.enc

# Расшифровка с предоставленным ключом

Используйте ключ из шифрования
cryptocore --algorithm aes --mode cbc --decrypt
--key 1a2b3c4d5e6f7890fedcba9876543210
--input secret.enc --output secret_decrypted.txt

# Шифрование с собственным ключом

cryptocore --algorithm aes --mode ctr --encrypt
--key 000102030405060708090a0b0c0d0e0f
--input data.txt --output data.enc

Аргументы командной строки
Аргумент Обязательный Описание
--algorithm Да Алгоритм шифрования (поддерживается только aes)
--mode Да Режим работы: ecb, cbc, cfb, ofb, ctr
--encrypt/--decrypt Да Операция для выполнения (взаимоисключающие)
--key Для расшифровки 16-байтовый ключ как шестнадцатеричная строка (опционально для шифрования)
--input Да Путь к входному файлу
--output Нет Путь к выходному файлу (автогенерируется, если опущен)
--iv Нет IV как шестнадцатеричная строка (только для расшифровки)

# Управление ключами
Автоматическая генерация ключей
Для шифрования: Ключ опционален. Если опущен, генерируется безопасный случайный ключ

Сгенерированные ключи выводятся только в stdout, нигде не сохраняются

# Важно: Вы должны сохранить сгенерированный ключ для расшифровки!

Обнаружение слабых ключей
Инструмент предупреждает о потенциально слабых ключах:

Все нули (0000...0000)

Все единицы (FFFF...FFFF)

Последовательные байты (00010203...)

# Повторяющиеся шаблоны (AAAA...AAAA, ABAB...ABAB)

# Пример предупреждения:


[WARNING] Предоставленный ключ кажется слабым!
[WARNING] Рекомендуется использовать более случайный ключ для лучшей безопасности.

# Форматы файлов
Для режимов с IV (CBC, CFB, OFB, CTR):
text
# Формат зашифрованного файла: [16-байтовый IV][Байты шифртекста]
Для режима ECB (без IV):
text
# Формат зашифрованного файла: [Только байты шифртекста]

Свойства безопасности
Генерация случайных чисел
Использует os.urandom() для всей криптографической случайности

Криптографически стойко на всех основных платформах:

Linux/macOS: Читает из /dev/urandom

Windows: Использует CryptGenRandom API

Проходит статистические тесты на случайность NIST (см. TESTING.md)

Безопасность ключей
Никогда не записывает сгенерированные ключи на диск

Ключи передаются только через stdout (видны пользователю)

# Пользователи отвечают за безопасное хранение ключей

# Тестирование
Базовые тесты

Запустите все тесты
python -m pytest tests/ -v

Тестируйте CSPRNG отдельно
python -m pytest tests/test_csprng.py -v

# Статистические тесты NIST
Для строгой проверки случайности запустите Набор статистических тестов NIST:

Сгенерируйте тестовые данные:

python -c "from src.csprng import generate_random_bytes;
open('test_data.bin', 'wb').write(generate_random_bytes(10000000))"
Запустите NIST STS (см. TESTING.md для подробных инструкций)

# Совместимость с OpenSSL

Зашифруйте с помощью CryptoCore, расшифруйте с помощью OpenSSL
cryptocore --algorithm aes --mode cbc --encrypt --input plain.txt --output cipher.bin

# Извлеките компоненты и расшифруйте с помощью OpenSSL
dd if=cipher.bin of=iv.bin bs=16 count=1
dd if=cipher.bin of=cipher_only.bin bs=16 skip=1
openssl enc -aes-128-cbc -d -K YOUR_KEY -iv $(xxd -p iv.bin) -in cipher_only.bin -out decrypted.txt

 # Структура проекта
##
cryptocore/
├── src/
│ ├── csprng.py
│ ├── cli_parser.py
│ ├── file_io.py
│ ├── modes/
│ └── cryptocore.py
├── tests/
├── requirements.txt
├── setup.py
├── README.md
└── TESTING.md
##
# Зависимости
Python 3.6+

pycryptodome

# (Опционально) nist-sts для статистического тестирования

Лицензия
[Укажите вашу лицензию здесь]

# Вопросы безопасности
Хранение ключей: Сгенерированные ключи отображаются только один раз. Используйте менеджер паролей.

# Права доступа к файлам: Защитите ваши файлы ключей и зашифрованные данные.

# Выбор режима: Избегайте ECB для конфиденциальных данных; предпочитайте CBC, CTR или другие безопасные режимы.

Случайность: CSPRNG использует криптографическую случайность, предоставляемую ОС.

Получение помощи
При проблемах или вопросах:

Проверьте файл TESTING.md для устранения неполадок

Проверьте совместимость с OpenSSL

Убедитесь, что используете правильный формат ключа (32 шестнадцатеричных символа)

 # 5. Обновленный requirements.txt
pycryptodome==3.20.0

# Опционально для тестирования NIST:
nist-sts>=0.2.0

# 6. Обновленный setup.py
from setuptools import setup, find_packages

setup(
name="cryptocore",
version="3.0.0",
packages=find_packages(),
install_requires=[
'pycryptodome>=3.20.0',
],
entry_points={
'console_scripts': [
'cryptocore=src.cryptocore:main',
],
},
python_requires='>=3.6',
classifiers=[
'Development Status :: 4 - Beta',
'Intended Audience :: Developers',
'Topic :: Security :: Cryptography',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 3',
'Programming Language :: Python :: 3.6',
'Programming Language :: Python :: 3.7',
'Programming Language :: Python :: 3.8',
'Programming Language :: Python :: 3.9',
'Programming Language :: Python :: 3.10',
],
)

# Инструкции по запуску

# 1. Активируйте виртуальное окружение
..venv\Scripts\Activate.ps1

 # 2. Установите обновленные зависимости
pip install -e .

# 3. Протестируйте новую функциональность
python -m pytest tests/test_csprng.py -v

# 4. Пример использования с генерацией ключа
Создайте тестовый файл
echo "Sensitive data that needs encryption" > document.txt

Зашифруйте с автоматической генерацией ключа
cryptocore --algorithm aes --mode ctr --encrypt --input document.txt --output document.enc

Скопируйте сгенерированный ключ из вывода и используйте для расшифровки
cryptocore --algorithm aes --mode ctr --decrypt --key СКОПИРУЙТЕ_КЛЮЧ_ЗДЕСЬ --input document.enc --output document_decrypted.txt

Проверьте, что файлы идентичны
diff document.txt document_decrypted.txt

# 8. Генерация тестовых данных для NIST
Для выполнения требований NIST тестирования:

python

Создайте файл generate_nist_data.py
from src.csprng import generate_random_bytes

Генерация 100MB тестовых данных
size_mb = 100
size_bytes = size_mb * 1024 * 1024

print(f"Generating {size_mb}MB of random data for NIST testing...")

with open('nist_random_data.bin', 'wb') as f:
chunk_size = 65536 # 64KB chunks
written = 0


while written < size_bytes:
    chunk = generate_random_bytes(min(chunk_size, size_bytes - written))
    f.write(chunk)
    written += len(chunk)
    
    # Progress indicator
    if written % (10 * 1024 * 1024) == 0:  # Every 10MB
        print(f"  {written / (1024*1024):.1f}MB / {size_mb}MB")
print(f"Done! Generated {written} bytes in 'nist_random_data.bin'")

CryptoCore - Криптографический инструмент
Комплексный инструмент командной строки для криптографии с:

AES-128 шифрованием/расшифровкой (режимы ECB, CBC, CFB, OFB, CTR)

Безопасной генерацией ключей с использованием CSPRNG

Хэш-функциями (SHA-256, SHA3-256), реализованными с нуля

# Проверкой целостности файлов

Возможности
Шифрование/Расшифровка
Алгоритмы: AES-128

Режимы: ECB, CBC, CFB, OFB, CTR

Управление ключами: Автоматическая безопасная генерация ключей

# Обработка IV: Безопасные случайные IV с правильным форматированием файлов

Дополнение: PKCS#7 для режимов ECB и CBC

Хэш-функции
SHA-256: Реализована с нуля в соответствии с NIST FIPS 180-4

SHA3-256: Реализована с нуля с использованием губчатой конструкции Keccak

Потоковая обработка: Обрабатывает файлы частями для постоянного использования памяти

Совместимость: Совместима со стандартными инструментами (sha256sum, sha3sum)

# Установка
Установите из исходного кода
pip install -e .

# Или вручную
pip install -r requirements.txt

Быстрый старт
Шифрование

# Зашифруйте с автогенерированным ключом
cryptocore --algorithm aes --mode cbc --encrypt --input secret.txt --output secret.enc

Зашифруйте с предоставленным ключом
cryptocore --algorithm aes --mode ctr --encrypt --key 000102030405060708090a0b0c0d0e0f --input data.txt --output data.enc

Расшифровка

Расшифруйте с ключом
cryptocore --algorithm aes --mode cbc --decrypt --key YOUR_KEY --input secret.enc --output secret.txt

# Вычисление хэша

Вычислите хэш SHA-256
cryptocore dgst --algorithm sha256 --input file.txt

Вычислите хэш SHA3-256 и сохраните в файл
cryptocore dgst --algorithm sha3-256 --input large_file.iso --output hash.txt

Хэш из stdin
cat file.txt | cryptocore dgst --algorithm sha256 --input -

# Справочник команд
Шифрование/Расшифровка (Режим по умолчанию)

cryptocore [--algorithm aes] --mode MODE (--encrypt|--decrypt) [--key HEX_KEY] --input FILE [--output FILE] [--iv HEX_IV]

# Режим вычисления хэша

cryptocore dgst --algorithm (sha256|sha3-256) --input FILE [--output FILE]

Хэш-алгоритмы
SHA-256
Стандарт: NIST FIPS 180-4

Вывод: 256 бит (32 байта, 64 шестнадцатеричных символа)

Реализация: С нуля с использованием конструкции Merkle-Damgård

Протестировано: Тестовые векторы NIST

SHA3-256
Стандарт: NIST FIPS 202 (Keccak)

Вывод: 256 бит (32 байта, 64 шестнадцатеричных символа)

Реализация: С нуля с использованием губчатой конструкции

Протестировано: Известные тестовые векторы

Примеры
Проверка целостности файлов

Создайте хэш исходного файла
cryptocore dgst --algorithm sha256 --input original.iso --output original.sha256

Позже, проверьте, что файл не изменился
cryptocore dgst --algorithm sha256 --input downloaded.iso | diff - original.sha256

Комбинированное шифрование и проверка целостности

Создайте хэш открытого текста
cryptocore dgst --algorithm sha256 --input document.txt --output document.hash

# Зашифруйте файл
cryptocore --algorithm aes --mode cbc --encrypt --input document.txt --output document.enc

Расшифруйте и проверьте целостность
cryptocore --algorithm aes --mode cbc --decrypt --key YOUR_KEY --input document.enc --output document.dec
cryptocore dgst --algorithm sha256 --input document.dec | diff - document.hash

# Тестирование
Запустите все тесты

python -m pytest tests/ -v

# Конкретные наборы тестов

# Тестируйте хэш-функции
python -m pytest tests/test_hash.py -v

Тестируйте шифрование
python -m pytest tests/test_modes.py -v

# Тестируйте CSPRNG
python -m pytest tests/test_csprng.py -v

Тестовые векторы NIST
Реализации проходят все тестовые векторы NIST:

# SHA-256: Тесты из FIPS 180-4

# SHA3-256: Тесты из FIPS 202

Тестирование совместимости


Сравните с системными инструментами
cryptocore dgst --algorithm sha256 --input test.txt > our_hash.txt
sha256sum test.txt > system_hash.txt
diff our_hash.txt system_hash.txt

# Детали реализации
Реализация SHA-256
Дополнение: Дополнение SHA-256 (добавить '1', нули, 64-битная длина)

Обработка блоков: 512-битные блоки

# Функция сжатия: 64 раунда с константами раундов

Расширение слов: Расширение расписания сообщений

Операции: Побитовые вращения, XOR, AND, NOT, сложение по модулю 2³²

# Реализация SHA3-256
Губчатая конструкция: Скорость 1088 бит, емкость 512 бит

Перестановка Keccak-f[1600]: 24 раунда

Состояние: Массив 5×5 из 64-битных слов

# Операции: Шаги θ, ρ, π, χ, ι

Производительность
Реализации оптимизированы для ясности и корректности, а не для скорости. Для больших файлов:

# Обрабатывает данные частями по 8KB

Постоянное использование памяти независимо от размера файла

Совместимо с потоковыми приложениями

# Вопросы безопасности
Хэш-функции
# SHA-256: Широко используется, считается безопасной

# SHA3-256: Хэш-функция следующего поколения, устойчива к атакам на расширение длины

Обе: Реализованы в соответствии со спецификацией, не оптимизированные версии

# Случайность
Генерация ключей использует os.urandom()

#  Генерация IV использует криптографически стойкий ГСЧ

Обнаружение слабых ключей предупреждает о небезопасных шаблонах

# Структура проекта
#
cryptocore/
├── src/
│ ├── hash/
│ │ ├── sha256.py
│ │ ├── sha3_256.py
│ │ └── utils.py
│ ├── modes/
│ ├── csprng.py
│ ├── cli_parser.py
│ └── cryptocore.py
├── tests/
├── requirements.txt
└── README.md
#
# Зависимости
Python 3.6+

# pycryptodome (для AES шифрования)

# Лицензия
[Укажите вашу лицензию здесь]

# Благодарности
NIST за криптографические стандарты

Криптографическому сообществу за тестовые векторы

# Преподавателям курса за руководство по проекту

Тесты хэш-функций
python -m pytest tests/test_hash.py::TestSHA256 -v
python -m pytest tests/test_hash.py::TestSHA3_256 -v
python -m pytest tests/test_hash.py::TestNISTVectors -v

# Тесты CLI
python -m pytest tests/test_hash.py::TestCLIHash -v

# Тестирование производительности

# Измерьте время вычисления хэша
time cryptocore dgst --algorithm sha256 --input large_file.iso

# Сравните с системными инструментами
time sha256sum large_file.iso

# 5. Тестовые векторы (опционально)
Создайте файл tests/test_vectors/sha256.json:

{
"test_vectors": [
{
"message": "",
"hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
},
{
"message": "abc",
"hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
},
{
"message": "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
"hash": "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
}
]
}

##6. Инструкции по запуску

Установка и тестирование
.\venv\Scripts\Activate.ps1
pip install -e .
python -m pytest tests/test_hash.py -v

Примеры использования
echo "Test data" > test.txt

Хэширование
cryptocore dgst --algorithm sha256 --input test.txt
cryptocore dgst --algorithm sha3-256 --input test.txt --output hash.txt

Проверка с системными утилитами (если доступны)
cryptocore dgst --algorithm sha256 --input test.txt > our_hash.txt

На Linux: sha256sum test.txt > system_hash.txt
diff our_hash.txt system_hash.txt
CryptoCore - Криптографический инструмент
Комплексный инструмент командной строки для криптографии с:

AES-128 шифрованием/расшифровкой (режимы ECB, CBC, CFB, OFB, CTR)

Безопасной генерацией ключей с использованием CSPRNG

Хэш-функциями (SHA-256, SHA3-256), реализованными с нуля

HMAC (код аутентификации сообщений на основе хэша) для проверки подлинности данных

AES-CMAC (опциональная дополнительная функция)

Возможности
Шифрование/Расшифровка
Алгоритмы: AES-128

Режимы: ECB, CBC, CFB, OFB, CTR

Управление ключами: Автоматическая безопасная генерация ключей

Обработка IV: Безопасные случайные IV с правильным форматированием файлов

Хэш-функции
SHA-256: Реализована с нуля в соответствии с NIST FIPS 180-4

SHA3-256: Реализована с нуля с использованием губчатой конструкции Keccak

Коды аутентификации сообщений (MAC)
HMAC-SHA256: Реализован с нуля в соответствии с RFC 2104

AES-CMAC: Опциональная реализация в соответствии с NIST SP 800-38B

Поддержка ключей: Ключи произвольной длины для HMAC, 16-байтовые ключи для AES-CMAC

Проверка: Встроенная проверка с подробными сообщениями об ошибках

Потоковая обработка: Обрабатывает большие файлы частями для постоянного использования памяти

# Установка
Установите из исходного кода
pip install -e .

Или вручную
pip install -r requirements.txt

# Быстрый старт
# Шифрование

Зашифруйте с автогенерированным ключом
cryptocore --algorithm aes --mode cbc --encrypt --input secret.txt --output secret.enc

Вычисление хэша

Вычислите хэш SHA-256
cryptocore dgst --algorithm sha256 --input file.txt

Вычислите хэш SHA3-256
cryptocore dgst --algorithm sha3-256 --input file.txt --output hash.txt

Генерация и проверка HMAC

Сгенерируйте HMAC
cryptocore dgst --algorithm sha256 --hmac --key YOUR_KEY_HEX --input message.txt

Проверьте HMAC
cryptocore dgst --algorithm sha256 --hmac --key YOUR_KEY_HEX --input message.txt --verify expected_hmac.txt

Сгенерируйте и сохраните HMAC
cryptocore dgst --algorithm sha256 --hmac --key YOUR_KEY_HEX --input message.txt --output message.hmac

Справочник команд HMAC
Базовая генерация HMAC

cryptocore dgst --algorithm sha256 --hmac --key <hex_key> --input <file>

# HMAC с выходным файлом

cryptocore dgst --algorithm sha256 --hmac --key <hex_key> --input <file> --output <hmac_file>

# Проверка HMAC

cryptocore dgst --algorithm sha256 --hmac --key <hex_key> --input <file> --verify <hmac_file>

AES-CMAC (Дополнительная функция)

cryptocore dgst --algorithm sha256 --cmac --key <16_byte_hex_key> --input <file>

Форматы ключей
Для HMAC:
Формат: Шестнадцатеричная строка

Длина: Произвольная (поддерживается любая длина)

Пример: 00112233445566778899aabbccddeeff

# Для AES-CMAC:
Формат: Шестнадцатеричная строка

Длина: 32 символа (16 байт)

Пример: 2b7e151628aed2a6abf7158809cf4f3c

# Свойства безопасности HMAC
На основе RFC 2104:
Обработка ключей: Ключи длиннее размера блока хэшируются, более короткие ключи дополняются нулями

Конструкция: HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))

Безопасность: Доказана безопасность, если базовая хэш-функция безопасна

Устойчивость: Устойчив к атакам на расширение длины

Особенности проверки:
Сравнение за постоянное время: Предотвращает атаки по времени

Подробные сообщения об ошибках: Помогает диагностировать сбои проверки

Гибкий разбор ввода: Принимает различные форматы файлов HMAC

Примеры
Целостность и подлинность файлов

# Создайте HMAC важного документа
cryptocore dgst --algorithm sha256 --hmac --key $(cat secret.key) --input document.pdf --output document.pdf.hmac

Позже, проверьте, что документ не был изменен
cryptocore dgst --algorithm sha256 --hmac --key $(cat secret.key) --input document.pdf --verify document.pdf.hmac

Комбинированное шифрование и аутентификация

Сгенерируйте случайный ключ для шифрования
cryptocore --algorithm aes --mode cbc --encrypt --input data.txt --output data.enc

# Сохраните отображенный ключ!
Создайте HMAC шифртекста для целостности
cryptocore dgst --algorithm sha256 --hmac --key $(cat hmac.key) --input data.enc --output data.enc.hmac

Проверьте перед расшифровкой
cryptocore dgst --algorithm sha256 --hmac --key $(cat hmac.key) --input data.enc --verify data.enc.hmac
cryptocore --algorithm aes --mode cbc --decrypt --key ENCRYPTION_KEY --input data.enc --output data.dec

# Тестирование реализации HMAC

Тестируйте с тестовыми векторами RFC 4231
python -c "
from src.mac import HMAC
key = bytes([0x0b] * 20)
message = b'Hi There'
hmac = HMAC(key, 'sha256')
print('HMAC:', hmac.compute_hex(message))
print('Expected: b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7')
"

# Тестирование
Запустите все тесты

python -m pytest tests/ -v

Конкретные наборы тестов

# Тестируйте функциональность HMAC
python -m pytest tests/test_hmac.py -v

Тестируйте тестовые векторы RFC 4231
python -m pytest tests/test_hmac.py::TestHMAC::test_rfc_4231_test_case_1 -v

Тестируйте CLI команды HMAC
python -m pytest tests/test_hmac.py::TestCLIHMAC -v


## Детали реализации
Реализация HMAC
Спецификация: Соответствует RFC 2104

Хэш-функция: Использует реализацию SHA-256 из Sprint 4

Размер блока: 64 байта для SHA-256

Обработка ключей: Автоматически обрабатывает ключи любой длины

Потоковая обработка: Поддерживает обработку больших файлов частями

Постоянное время: Использует сравнение за постоянное время для проверки

# Обработка файлов
Размер части: Части по 8KB для эффективного использования памяти

Бинарный режим: Все файлы читаются/записываются в бинарном режиме

Большие файлы: Может обрабатывать файлы больше доступной памяти

Потоковая обработка: Вычисляет HMAC без загрузки всего файла в память

Вопросы безопасности
Безопасность ключей
Ключи HMAC должны храниться в секрете

# Используйте криптографически стойкие случайные ключи

Храните ключи безопасно (менеджер паролей, аппаратный модуль безопасности)

Безопасность проверки
Использует сравнение за постоянное время для предотвращения атак по времени

Подробные сообщения об ошибках не раскрывают конфиденциальную информацию

Проверка безопасно завершается с ошибкой при любом несоответствии

# Безопасность алгоритмов
HMAC-SHA256 широко считается безопасным

AES-CMAC предоставляет аналогичные гарантии безопасности

Оба являются стандартизированными и хорошо проверенными алгоритмами

# Структура проекта
#
cryptocore/
├── src/
│ ├── mac/
│ │ ├── hmac.py
│ │ ├── cmac.py
│ │ └── utils.py
│ ├── hash/
│ ├── modes/
│ ├── csprng.py
│ └── cryptocore.py
├── tests/
├── requirements.txt
└── README.md
#
## CryptoCore - Продвинутый криптографический инструмент
Комплексный инструмент командной строки для криптографии с поддержкой аутентифицированного шифрования.

 # Возможности
 Шифрование/Расшифровка
Стандартные режимы: ECB, CBC, CFB, OFB, CTR

Аутентифицированные режимы: GCM (Galois/Counter Mode), Encrypt-then-MAC

Управление ключами: Безопасная случайная генерация ключей

Обработка IV/Nonce: Автоматическая генерация с правильным форматированием

# Аутентифицированное шифрование (AEAD)
GCM: Соответствует NIST SP 800-38D, 12-байтовый nonce, 16-байтовый тег

Encrypt-then-MAC: Комбинирование любого режима шифра с HMAC-SHA256

Ассоциированные данные: Поддержка AAD произвольной длины

Катастрофический отказ: Нет вывода при неудачной аутентификации

# Хэш-функции
SHA-256: Реализация FIPS 180-4

SHA3-256: Губчатая конструкция Keccak

HMAC-SHA256: Соответствует RFC 2104

AES-CMAC: NIST SP 800-38B (дополнительно)

# Установка
Клонируйте репозиторий
git clone https://github.com/yourusername/cryptocore.git
cd cryptocore

# Установите зависимости
pip install -r requirements.txt

Установите в режиме разработки
pip install -e .

Быстрый старт
Шифрование GCM

# Зашифруйте с автогенерированным ключом
cryptocore --algorithm aes --mode gcm --encrypt
--input secret.txt
--output secret.gcm
--aad aabbccddeeff

# Вывод включает сгенерированный ключ и nonce
Расшифровка GCM

Расшифруйте с сохраненным ключом
cryptocore --algorithm aes --mode gcm --decrypt
--key YOUR_KEY_HERE
--input secret.gcm
--output secret_decrypted.txt
--aad aabbccddeeff

Encrypt-then-MAC

Зашифруйте с защитой целостности
cryptocore --algorithm aes --mode etm --encrypt
--key 32_BYTE_KEY_HEX
--input data.txt
--output data.etm
--aad metadata123

# Расшифруйте с проверкой
cryptocore --algorithm aes --mode etm --decrypt
--key 32_BYTE_KEY_HEX
--input data.etm
--output data_decrypted.txt
--aad metadata123

Полное использование
Режим GCM

# Шифрование с указанием nonce
cryptocore --algorithm aes --mode gcm --encrypt
--key 00112233445566778899aabbccddeeff
--iv 000000000000000000000000
--input plain.txt
--output cipher.gcm
--aad associated_data_hex

# Расшифровка (читает nonce из файла)
cryptocore --algorithm aes --mode gcm --decrypt
--key 00112233445566778899aabbccddeeff
--input cipher.gcm
--output plain.txt
--aad associated_data_hex

Режим Encrypt-then-MAC


Использование CBC как базового режима
cryptocore --algorithm aes --mode etm --encrypt
--key 64_HEX_CHARS_32_BYTES
--input file.txt
--output file.etm

# С явным IV
cryptocore --algorithm aes --mode etm --decrypt
--key 64_HEX_CHARS_32_BYTES
--iv IV_HEX_32_CHARS
--input file.etm
--output file.txt

# Форматы файлов
Формат GCM
text
[12-байтовый nonce][шифртекст][16-байтовый тег аутентификации]

# Формат Encrypt-then-MAC
text
[16-байтовый IV (опционально)][шифртекст][32-байтовый тег HMAC]

Тестирование


# Запустите все тесты
python -m pytest tests/ -v

Тестируйте GCM отдельно
python -m pytest tests/test_gcm.py -v

Тестируйте Encrypt-then-MAC
python -m pytest tests/test_encrypt_then_mac.py -v

Тестируйте свойства безопасности
python -m pytest tests/test_gcm.py::TestGCM::test_ciphertext_tamper -v

Функции безопасности

Обработка неудачной аутентификации
Нет частичного вывода: Файлы не создаются при неудачной аутентификации

# Чистый выход: Ненулевые коды выхода с описательными ошибками

Защита от атак по времени: Сравнения за постоянное время

Безопасность ключей
Обнаружение слабых ключей: Предупреждает о предсказуемых ключах

Безопасная генерация: Криптографически случайные ключи через ОС RNG

# Разделение ключей: Разные ключи для шифрования и MAC

Случайность
Уникальность nonce: Гарантированная уникальность nonce для GCM

Случайность IV: Безопасные случайные IV для всех режимов

# Соответствие NIST: Проходит статистические тесты на случайность

# Примеры
Целостность файлов с аутентификацией

1. Создайте аутентифицированное зашифрованное резервное копирование
cryptocore --algorithm aes --mode gcm --encrypt
--input database.db
--output backup.enc
--aad $(date -I)

2. Проверьте и восстановите
cryptocore --algorithm aes --mode gcm --decrypt
--key YOUR_KEY
--input backup.enc
--output restored.db
--aad 2024-01-15

Безопасный обмен сообщениями

Alice шифрует с AAD, содержащим метаданные
cryptocore --mode gcm --encrypt
--input message.txt
--output message.enc
--aad "from=alice&to=bob&date=2024-01-15"

Bob расшифровывает и проверяет метаданные
cryptocore --mode gcm --decrypt
--key SHARED_KEY
--input message.enc
--output message.txt
--aad "from=alice&to=bob&date=2024-01-15"

Совместимость с OpenSSL

Зашифруйте с помощью CryptoCore
cryptocore --mode gcm --encrypt --key KEY --input plain.txt --output crypto.gcm

Расшифруйте с помощью OpenSSL (если совместимо)
openssl enc -aes-256-gcm -d -K KEY -iv $(head -c12 crypto.gcm | xxd -p)
-aad AAD_HEX -in <(tail -c+13 crypto.gcm | head -c-16) -out plain.txt

Вопросы безопасности
Управление ключами: Всегда используйте криптографически случайные ключи

Повторное использование Nonce: Никогда не используйте повторно nonce с одним и тем же ключом в GCM

Целостность AAD: AAD аутентифицируется, но не шифруется

Выбор режима: Используйте GCM или Encrypt-then-MAC для конфиденциальных данных

Размер ключа: Используйте 256-битные ключи, когда это возможно

Устранение неполадок
Распространенные проблемы
"Аутентификация не удалась": Несоответствие AAD или изменение данных

"Недопустимая длина ключа": GCM требует 16/24/32-байтовые ключи

"Файл слишком короткий": Поврежденный или неполный зашифрованный файл

"Недопустимый hex": Ключ/IV/AAD должны быть допустимыми шестнадцатеричными значениями

# Режим отладки

Добавьте подробный вывод
python -m src.cryptocore --mode gcm --encrypt --input test.txt -v

Вывод ключей (Спринт 7)
Обзор
CryptoCore теперь поддерживает безопасный вывод ключей из паролей с использованием PBKDF2-HMAC-SHA256 (RFC 2898) и функций иерархии ключей.

# Быстрый старт
Базовый вывод ключей
Выведите ключ с указанной солью
cryptocore derive --password "MySecurePassword123!"
--salt 1234567890abcdef1234567890abcdef
--iterations 100000
--length 32

# Выведите ключ с автогенерированной солью
cryptocore derive --password "AnotherPassword"
--iterations 500000
--length 16

Полное использование
Вывод ключей PBKDF2
bash

Базовый вывод (вывод: KEY_HEX SALT_HEX)
cryptocore derive --password <password>
--salt <hex_salt>
--iterations <count>
--length <bytes>

# Сохраните в файл
cryptocore derive --password "app_key"
--salt fixedappsalt
--iterations 100000
--length 32
--output derived_key.txt

Выведите сырой бинарный ключ
cryptocore derive --password "secret"
--salt 1234567890abcdef
--iterations 10000
--length 16
--raw
--output key.bin

Параметры команд
Опция Обязательный По умолчанию Описание
--password Да - Строка пароля
--salt Нет Автогенерируется Соль как шестнадцатеричная строка
--iterations Нет 100,000 Количество итераций
--length Нет 32 Длина ключа в байтах
--algorithm Нет pbkdf2 Алгоритм KDF
--output Нет stdout Выходной файл
--raw Нет false Вывод сырых бинарных данных

Рекомендации по безопасности

# Количество итераций
Минимум: 10,000 итераций

Рекомендуется: 100,000+ итераций

Высокая безопасность: 1,000,000+ итераций

# Требования к соли
Всегда используйте случайную соль для каждого пароля

Минимальная длина: 16 байт (128 бит)

# Рекомендуется: 32 байта (256 бит)

Рекомендации по паролям
Используйте сильные, сложные пароли

Минимум 12 символов

Включайте прописные, строчные буквы, цифры, символы

Хранение ключей
Никогда не храните пароли - храните полученные ключи

Используйте безопасные решения для хранения ключей

Рассмотрите аппаратные модули безопасности для производства

Примеры

# Сгенерируйте ключ шифрования

cryptocore derive --password "DatabaseMasterKey2024!"
--iterations 500000
--length 32
--output db_encryption_key.txt

Создайте иерархию ключей
python
from src.kdf.hkdf import derive_key

Мастер-ключ из PBKDF2
master_key = bytes.fromhex("your_derived_key_hex")

Выведите ключи для конкретного использования
encryption_key = derive_key(master_key, "database_encryption", 32)
auth_key = derive_key(master_key, "api_authentication", 32)
signing_key = derive_key(master_key, "jwt_signing", 32)

Тестовые векторы RFC 6070


Тестовый вектор 1
cryptocore derive --password "password"
--salt 73616c74
--iterations 1
--length 20

Ожидается: 0c60c80f961f0e71f3a9b524af6012062fe037a6
Тестовый вектор 2
cryptocore derive --password "password"
--salt 73616c74
--iterations 2
--length 20

Ожидается: ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957
Технические детали
Реализация PBKDF2
Стандарт: Соответствует RFC 2898

# Хэш-функция: HMAC-SHA256 (с нуля)

Растяжение ключа: Настраиваемое количество итераций

Поддержка соли: Соли произвольной длины

Функция иерархии ключей
Функция: derive_key(master_key, context, length)

Метод: Детерминированный вывод на основе HMAC

Разделение контекста: Уникальные ключи для разных целей

Произвольная длина: Поддерживает любую длину ключа

# Тестирование
Запустите все тесты

python -m pytest tests/test_kdf.py -v

Тестовые векторы RFC 6070
python -m pytest tests/test_kdf.py::TestPBKDF2::test_rfc_6070_vector_1 -v

Тесты CLI
python -m pytest tests/test_kdf.py::TestCLIDerive -v

# Тесты производительности
python -m pytest tests/test_kdf.py::TestPBKDF2::test_performance -v

Совместимость с OpenSSL

Сравните с OpenSSL
cryptocore derive --password "test"
--salt 1234567890abcdef
--iterations 10000
--length 32
--raw > cryptocore_key.bin

openssl kdf -keylen 32
-kdfopt pass:test
-kdfopt hexsalt:1234567890abcdef
-kdfopt iter:10000
PBKDF2 > openssl_key.bin

diff cryptocore_key.bin openssl_key.bin

# Соображения производительности
Количество итераций против времени
Итерации Примерное время (1 ядро) Уровень безопасности
10,000 0.01s Базовый
100,000 0.1s Стандартный
500,000 0.5s Высокий
1,000,000 1.0s Очень высокий

# Использование памяти
Постоянная память: Обрабатывает частями фиксированного размера

Нет кэширования на диске: Все операции в памяти

Безопасная очистка: Пароли очищаются после использования

Распространенные проблемы

"Недопустимая шестнадцатеричная соль"


# Ошибка: Соль должна быть допустимым шестнадцатеричным значением
cryptocore derive --password "test" --salt "not_hex"

Решение: Используйте hex или позвольте инструменту сгенерировать соль
cryptocore derive --password "test" --salt "1234567890abcdef"

# Предупреждение о малом количестве итераций


Появляется предупреждение для < 100,000 итераций
cryptocore derive --password "test" --iterations 1000

Решение: Увеличьте количество итераций
cryptocore derive --password "test" --iterations 100000

Пароль со специальными символами


# Используйте кавычки для интерпретации оболочкой
cryptocore derive --password "My!Pass@word#123$"

Или экранируйте символы
cryptocore derive --password My!Pass@word#123$

Ссылки
RFC 2898: Спецификация PBKDF2

RFC 6070: Тестовые векторы PBKDF2

NIST SP 800-132: Вывод ключей на основе паролей

OWASP Cheat Sheet по хранению паролей

# Инструкция по установке и тестированию:
Установите обновленный пакет:
pip install -e .

Запустите тесты:

python run_tests.py

Или отдельно тесты KDF:
python -m pytest tests/test_kdf.py -v

# Примеры использования:

Базовое получение ключа
cryptocore derive --password "MyPassword123!" --iterations 100000

RFC тестовые векторы
cryptocore derive --password "password" --salt 73616c74 --iterations 1 --length 20

# Сохранение в файл
cryptocore derive --password "app_key" --iterations 500000 --output app_key.txt

Запустите пример:
python examples/key_derivation_example.py

CryptoCore 🛡️
https://img.shields.io/badge/python-3.6%252B-blue.svg
https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/tests-passing-brightgreen.svg

# CryptoCore - это комплексная криптографическая библиотека и инструмент командной строки, реализованные с нуля для образовательных целей. Он предоставляет криптографические примитивы производственного уровня с акцентом на безопасность, корректность и обучение.

# Возможности
Шифрование/Расшифровка
AES-128 с несколькими режимами:

Базовые: ECB, CBC, CFB, OFB, CTR

Аутентифицированные: GCM (Galois/Counter Mode), Encrypt-then-MAC

Автоматическая генерация ключей с безопасным ГСЧ

Обработка IV/Nonce с правильными форматами файлов

# Дополнение PKCS#7 там, где это требуется

Поддержка ассоциированных данных (AAD) для аутентифицированных режимов

Хэш-функции (Реализованы с нуля)
SHA-256 (NIST FIPS 180-4)

SHA3-256 (губчатая конструкция Keccak)

Поддержка потоковой обработки для больших файлов

Соответствие тестовым векторам NIST

# Коды аутентификации сообщений
HMAC-SHA256 (RFC 2104)

AES-CMAC (NIST SP 800-38B) - дополнительная функция

Проверка за постоянное время для предотвращения атак по времени

Потоковый HMAC для больших файлов

Вывод ключей (Спринт 7)
PBKDF2-HMAC-SHA256 (RFC 2898)

Функции иерархии ключей для вывода подчиненных ключей

Соответствие тестовым векторам RFC 6070

Безопасная генерация и управление солью

Криптографически стойкий ГСЧ
Случайность, предоставляемая ОС (os.urandom())

Обнаружение слабых ключей и предупреждения

Статистическая проверка случайности

# Быстрый старт
Установка
Клонируйте репозиторий
git clone https://github.com/yourusername/cryptocore.git
cd cryptocore

Установите в режиме разработки
pip install -e .

Установите зависимости
pip install -r requirements.txt

Базовое использование

# Зашифруйте файл (автогенерирует ключ)
cryptocore --algorithm aes --mode cbc --encrypt --input secret.txt --output secret.enc

Сохраните отображенный ключ!
Расшифруйте файл
cryptocore --algorithm aes --mode cbc --decrypt --key YOUR_KEY --input secret.enc --output secret.txt

# Вычислите хэш SHA-256
cryptocore dgst --algorithm sha256 --input file.iso

Сгенерируйте HMAC для аутентификации
cryptocore dgst --algorithm sha256 --hmac --key YOUR_KEY --input firmware.bin

Выведите ключ из пароля
cryptocore derive --password "MySecurePassword123!" --iterations 100000 --length 32

# Документация
Полная документация доступна в каталоге docs/:

API Reference - Полная документация API

User Guide - Использование CLI с примерами

Development Guide - Разработка и внесение вклада

Examples - Примеры кода для распространенных случаев использования

CryptoCore включает комплексный набор тестов:

# Запустите все тесты
python run_tests.py

Запустите конкретные категории тестов
python run_tests.py --unit # Модульные тесты
python run_tests.py --integration # Интеграционные тесты
python run_tests.py --performance # Тесты производительности
python run_tests.py --interop # Тесты совместимости

Запустите напрямую с помощью pytest
python -m pytest tests/ -v

Сгенерируйте отчет о покрытии
python -m pytest --cov=src tests/ --cov-report=html

# Структура проекта
#
cryptocore/
├── src/ # Исходный код
│ ├── cryptocore.py # Основная точка входа CLI
│ ├── cli_parser.py # Разбор командной строки
│ ├── file_io.py # Утилиты ввода-вывода файлов
│ ├── csprng.py # Криптографически стойкий ГСЧ
│ ├── modes/ # Режимы шифрования
│ ├── hash/ # Хэш-функции (с нуля)
│ ├── mac/ # Коды аутентификации сообщений
│ └── kdf/ # Функции вывода ключей
├── tests/ # Комплексный набор тестов
│ ├── unit/ # Модульные тесты
│ ├── integration/ # Интеграционные тесты
│ ├── vectors/ # Тестовые векторы с известными ответами
│ └── run_tests.py # Запускатор тестов
├── docs/ # Документация
│ ├── API.md
│ ├── USERGUIDE.md
│ └── DEVELOPMENT.md
├── examples/ # Примеры использования
├── requirements.txt # Зависимости Python
├── setup.py # Настройка пакета
├── pyproject.toml # Конфигурация сборки
├── .pylintrc # Качество кода
├── CHANGELOG.md # История версий
├── CONTRIBUTING.md # Рекомендации по внесению вклада
├── SECURITY.md # Политика безопасности
├── CODE_OF_CONDUCT.md # Правила сообщества
└── LICENSE # Лицензия MIT
#
# Реализованные защиты
Операции за постоянное время для предотвращения атак по времени

Безопасная очистка памяти для конфиденциальных данных

Валидация ввода всех параметров

# Аутентификация перед расшифровкой (GCM, HMAC)

Нет утечки информации в сообщениях об ошибках

Рекомендации по безопасности
Используйте аутентифицированное шифрование (GCM или Encrypt-then-MAC) для конфиденциальных данных

Никогда не используйте повторно nonce с одним и тем же ключом в режиме GCM

# Используйте криптографически стойкие случайные ключи

Выполняйте проверку аутентификации перед использованием данных

Используйте PBKDF2 с ≥100,000 итерациями для вывода ключей

# Производительность
Бенчмарки (на типичном оборудовании)
text
PBKDF2-HMAC-SHA256:
1,000 итераций: 0.003s
10,000 итераций: 0.030s
100,000 итераций: 0.300s
500,000 итераций: 1.500s

Хэш-функции (1MB данных):
SHA-256: 0.050s (~20 MB/s)
SHA3-256: 0.080s (~12 MB/s)

Шифрование (AES-128 CBC, 1MB):
Шифрование: 0.020s (~50 MB/s)
Расшифровка: 0.020s (~50 MB/s)

Примечание: Это образовательные реализации. Производственные библиотеки значительно быстрее.

# Внесение вклада
Мы приветствуем вклад! Пожалуйста, ознакомьтесь с нашими Рекомендациями по внесению вклада для деталей.

Настройка разработки

Клонируйте и настройте среду разработки
git clone https://github.com/yourusername/cryptocore.git
cd cryptocore
python -m venv venv
source venv/bin/activate # Linux/macOS

.\venv\Scripts\Activate.ps1 # Windows
pip install -e .[dev]

# Стандарты кода
Следуйте руководству по стилю PEP 8

Пишите комплексные докстринги

Добавляйте подсказки типов для новых функций

Пишите тесты для новых функций

Обновляйте документацию

Ресурсы для обучения
Реализованные криптографические стандарты
AES: NIST FIPS 197

SHA-256: NIST FIPS 180-4

SHA3-256: NIST FIPS 202

GCM: NIST SP 800-38D

HMAC: RFC 2104

PBKDF2: RFC 2898

Полезные ссылки
Криптографические стандарты NIST

Репозиторий RFC

Книга "Cryptography Engineering"

# Вопросы безопасности
Важные замечания
Образовательная цель: CryptoCore в первую очередь предназначен для изучения криптографических реализаций.

Не валидирован FIPS: Реализации соответствуют спецификациям, но не сертифицированы.

Использование в производстве: Для производственных систем используйте валидированные библиотеки, такие как OpenSSL или libsodium.

Аудиты безопасности: Этот код не проходил формальные аудиты безопасности.

# Когда использовать CryptoCore
Изучение реализации криптографии

Образовательные демонстрации

Тестирование и сравнение

Некритичные приложения

# Когда использовать другие инструменты
Производственные системы (используйте OpenSSL, libsodium)

Соответствие нормативным требованиям (используйте библиотеки, валидированные FIPS)

Приложения высокой безопасности (используйте аппаратные модули безопасности)

Лицензия
CryptoCore выпущен под лицензией MIT. См. файл LICENSE для деталей.

Благодарности
NIST за криптографические стандарты

IETF за спецификации RFC

Криптографическому сообществу за тестовые векторы и руководство

Преподавателям курса за требования к проекту и обратную связь

Поддержка
Документация: См. каталог docs/

Проблемы: GitHub Issues

Безопасность: См. SECURITY.md для сообщения об уязвимостях

Инструкция по установке и тестированию:
Установите полный пакет:

pip install -e .[dev]

# Запустите все проверки:

python scripts/check_all.py

Запустите все тесты:

python run_tests.py

Проверьте документацию:

API документация
cat docs/API.md | head -50

Руководство пользователя
cat docs/USERGUIDE.md | head -50

Руководство разработчика
cat docs/DEVELOPMENT.md | head -50

# Запустите примеры:

python examples/basic_usage.py


