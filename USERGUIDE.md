### **2. `docs/USERGUIDE.md`**

```markdown
# Руководство пользователя CryptoCore

## Установка

### Установка из исходного кода
```bash
git clone https://github.com/Nikita21537/CryptoCore.git
cd CryptoCore
pip install -e .
Установка через pip (после релиза)
bash
pip install cryptocore
Базовое использование
Шифрование файла
bash
# AES-CBC с указанием ключа
cryptocore --algorithm aes --mode cbc --encrypt \
  --key 00112233445566778899aabbccddeeff \
  --input secret.txt \
  --output secret.enc

# AES-GCM с дополнительными аутентифицированными данными
cryptocore --algorithm aes --mode gcm --encrypt \
  --key 00112233445566778899aabbccddeeff \
  --input database.sql \
  --output database.enc \
  --aad "database_version_3.2"
Дешифрование файла
bash
# Дешифрование CBC
cryptocore --algorithm aes --mode cbc --decrypt \
  --key 00112233445566778899aabbccddeeff \
  --input secret.enc \
  --output secret_decrypted.txt

# Дешифрование GCM (проверка аутентификации)
cryptocore --algorithm aes --mode gcm --decrypt \
  --key 00112233445566778899aabbccddeeff \
  --input database.enc \
  --output database_decrypted.sql \
  --aad "database_version_3.2"
Хеширование файлов
bash
# SHA-256
cryptocore --algorithm sha256 --input file.txt

# SHA3-256
cryptocore --algorithm sha3_256 --input file.txt
HMAC
bash
# Генерация HMAC
cryptocore --algorithm hmac --key mysecret --input data.txt

# Проверка HMAC
cryptocore --algorithm hmac --key mysecret --verify expected_hmac --input data.txt
Получение ключей из пароля
bash
# Базовая деривация ключа
cryptocore derive --password "MySecurePassword" --salt 73616c74 --iterations 100000 --length 32

# Автоматическая генерация соли
cryptocore derive --password "AnotherPassword" --iterations 500000

# Сохранение ключа в файл
cryptocore derive --password "app_key" --salt fixedappsalt --output key.bin
Расширенные сценарии
Создание иерархии ключей
python
from cryptocore.kdf import derive_key

master_key = b'0' * 32
encryption_key = derive_key(master_key, "encryption", 32)
authentication_key = derive_key(master_key, "authentication", 32)
Работа с большими файлами
bash
# Шифрование файла > 1GB
cryptocore --algorithm aes --mode ctr --encrypt \
  --key $(cat secret.key) \
  --input large_video.mp4 \
  --output large_video.enc \
  --chunk-size 65536
Устранение неполадок
Ошибка "Invalid key length"
Убедитесь, что ключ имеет правильную длину:

AES-128: 16 байт (32 hex символа)

AES-192: 24 байта (48 hex символов)

AES-256: 32 байта (64 hex символа)

Ошибка "Authentication failed" (GCM)
Проверьте, что:

Ключ правильный

AAD совпадает с использованным при шифровании

Файл не был изменен

Ошибка "File not found"
Убедитесь, что входной файл существует

Проверьте права доступа к файлу

Рекомендации по безопасности
Управление ключами
Никогда не храните ключи в коде

Используйте безопасное хранилище ключей (HSM, KMS)

Регулярно ротируйте ключи

Выбор режимов шифрования
Используйте GCM или ChaCha20-Poly1305 для аутентифицированного шифрования

Избегайте ECB режима для реальных данных

Всегда используйте уникальные IV/Nonce для каждого шифрования

Безопасность паролей
Минимум 100,000 итераций для PBKDF2

Используйте уникальные соли для каждого пароля

Минимальная длина пароля: 12 символов

Быстрая шпаргалка
bash
# Шифрование
cryptocore -a aes -m gcm -e -k KEY -i IN -o OUT

# Дешифрование
cryptocore -a aes -m gcm -d -k KEY -i IN -o OUT

# Хеш
cryptocore -a sha256 -i FILE

# HMAC
cryptocore -a hmac -k KEY -i FILE

# Деривация ключа
cryptocore derive -p PASSWORD -s SALT -i 100000
Сравнение с другими инструментами
Операция	CryptoCore	OpenSSL	GPG
AES-GCM	cryptocore -a aes -m gcm	openssl aes-256-gcm	gpg -c
SHA-256	cryptocore -a sha256	openssl dgst -sha256	gpg --print-md
HMAC	cryptocore -a hmac	openssl dgst -hmac	N/A
PBKDF2	cryptocore derive	openssl kdf -pbkdf2	N/A
