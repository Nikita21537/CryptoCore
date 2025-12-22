# CryptoCore API Documentation

## Обзор

CryptoCore — это криптографическая библиотека, реализующая современные алгоритмы шифрования, хеширования и аутентификации.

## Модули

### Модуль: `cryptocore.aes`
Реализация алгоритма AES (Advanced Encryption Standard).

#### `encrypt_block(key: bytes, plaintext: bytes) -> bytes`
Шифрует один 16-байтовый блок с использованием AES-128.

**Параметры:**
- `key` (bytes): 16-байтовый ключ шифрования
- `plaintext` (bytes): 16-байтовый блок для шифрования

**Возвращает:**
- `bytes`: 16-байтовый зашифрованный блок

**Исключения:**
- `ValueError`: если длина ключа или plaintext некорректна

**Пример:**
```python
from cryptocore.aes import encrypt_block

key = b'0' * 16
plaintext = b'hello world!!!!!!'
ciphertext = encrypt_block(key, plaintext)
decrypt_block(key: bytes, ciphertext: bytes) -> bytes
Дешифрует один 16-байтовый блок с использованием AES-128.

Параметры:

key (bytes): 16-байтовый ключ шифрования

ciphertext (bytes): 16-байтовый зашифрованный блок

Возвращает:

bytes: 16-байтовый расшифрованный блок

Модуль: cryptocore.modes
Реализация режимов шифрования.

cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes
Шифрует данные в режиме CBC (Cipher Block Chaining).

Параметры:

key (bytes): ключ шифрования (16, 24 или 32 байта)

iv (bytes): вектор инициализации (16 байт)

plaintext (bytes): данные для шифрования

Возвращает:

bytes: зашифрованные данные

gcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = b'') -> tuple[bytes, bytes]
Шифрует данные в режиме GCM (Galois/Counter Mode) с аутентификацией.

Параметры:

key (bytes): ключ шифрования

plaintext (bytes): данные для шифрования

aad (bytes): дополнительные аутентифицированные данные (опционально)

Возвращает:

tuple[bytes, bytes]: (ciphertext, authentication_tag)

Модуль: cryptocore.hash
Хеш-функции.

sha256(data: bytes) -> bytes
Вычисляет SHA-256 хеш.

sha3_256(data: bytes) -> bytes
Вычисляет SHA3-256 хеш.

Модуль: cryptocore.mac
Функции аутентификации сообщений.

hmac_sha256(key: bytes, message: bytes) -> bytes
Вычисляет HMAC-SHA256.

cmac_aes(key: bytes, message: bytes) -> bytes
Вычисляет CMAC на основе AES.

Модуль: cryptocore.kdf
Функции получения ключей.

pbkdf2_hmac_sha256(password: bytes, salt: bytes, iterations: int, dklen: int) -> bytes
Реализация PBKDF2-HMAC-SHA256.

derive_key(master_key: bytes, context: str, length: int = 32) -> bytes
Деривация ключей из мастер-ключа.

Модуль: cryptocore.csprng
Криптографически безопасная генерация случайных чисел.

generate_random_bytes(length: int) -> bytes
Генерирует криптографически безопасные случайные байты.

#Диаграмма зависимостей
text
cryptocore.aes
    ├── cryptocore.modes
    │   ├── cryptocore.hash (для GCM)
    │   └── cryptocore.mac (для CMAC)
    ├── cryptocore.mac (база для HMAC)
    └── cryptocore.kdf (для получения ключей)
