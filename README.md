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
## Инструкции по установке и тестированию:
Скопируйте файлы в соответствующие директории вашего проекта.
Запустите тесты:
# Запуск unit тестов
python -m pytest tests/test_hmac.py -v
# Запуск интеграционных тестов
python -m pytest tests/integration/test_cli_hmac.py -v
# Запуск тестовых векторов
python tests/test_hmac_vectors.py
Пример использования:
# Генерация HMAC
python -m src.cli dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input README.md
# Верификация HMAC
python -m src.cli dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input README.md --verify hmac.txt
## Sprint 6: Authenticated Encryption (GCM & Encrypt-then-MAC)

### Новые возможности:
1. **GCM (Galois/Counter Mode)** - аутентифицированное шифрование
2. **Encrypt-then-MAC** - композитный режим аутентификации
3. **Associated Data (AAD)** - поддержка дополнительных аутентифицируемых данных

### Примеры использования GCM:


# Шифрование с AAD
cryptocore --algorithm aes --mode gcm --encrypt \
  --key 00112233445566778899aabbccddeeff \
  --input data.txt \
  --output encrypted.bin \
  --aad aabbccddeeff00112233445566778899

# Расшифрование
cryptocore --algorithm aes --mode gcm --decrypt \
  --key 00112233445566778899aabbccddeeff \
  --input encrypted.bin \
  --output decrypted.txt \
  --aad aabbccddeeff00112233445566778899
  Структура выходных файлов GCM:
Шифрование: nonce(12) || ciphertext || tag(16)

Расшифрование: проверка тега перед выводом данных

Важные предупреждения безопасности:
Никогда не используйте один nonce дважды с одним ключом!

При неудачной аутентификации данные не выводятся

AAD аутентифицируется, но не шифруется



## 11. **Деплой и тестирование**

1. **Установите зависимости:**

pip install -r requirements.txt
Запустите тесты:


python -m pytest tests/test_gcm.py -v
python -m pytest tests/test_aead.py -v
Запустите интеграционные тесты:


# Тест с OpenSSL (если установлен)
./tests/integration/test_openssl_compat.sh
Проверьте CLI:


# Создайте тестовые файлы
echo "Hello, CryptoCore GCM!" > test.txt

# Зашифруйте
python main.py --algorithm aes --mode gcm --encrypt \
  --key 000102030405060708090a0b0c0d0e0f \
  --input test.txt --output test.enc \
  --aad 0011223344556677

# Расшифруйте
python main.py --algorithm aes --mode gcm --decrypt \
  --key 000102030405060708090a0b0c0d0e0f \
  --input test.enc --output test.dec \
  --aad 0011223344556677

# Проверьте результат
cat test.dec
### **7. `SECURITY.md`**

```markdown
# Политика безопасности

## Сообщение об уязвимостях

Мы серьезно относимся к безопасности CryptoCore. Если вы обнаружили уязвимость, пожалуйста, сообщите об этом ответственно.

### Как сообщить
**НЕ СОЗДАВАЙТЕ ПУБЛИЧНЫЙ ISSUE**

Вместо этого:
1. Отправьте email на: `security@example.com` (замените на реальный email)
2. Включите:
   - Описание уязвимости
   - Шаги для воспроизведения
   - Возможное воздействие
   - Предложения по исправлению (если есть)
3. Мы ответим в течение **48 часов**

### Что ожидать
1. **Подтверждение:** Мы подтвердим получение отчета
2. **Расследование:** Мы исследуем уязвимость
3. **Исправление:** Мы разработаем исправление
4. **Раскрытие:** Мы опубликуем исправление и информацию об уязвимости

## Процесс реагирования на инциденты

1. **Оценка:** Определяем серьезность и влияние
2. **Содержание:** Ограничиваем распространение информации
3. **Исправление:** Разрабатываем и тестируем патч
4. **Выпуск:** Выпускаем безопасную версию
5. **Коммуникация:** Информируем пользователей
6. **Пост-мортем:** Анализируем и улучшаем процессы

## Уровни серьезности

### Критический (Critical)
- Компрометация ключей шифрования
- Обход аутентификации
- Утечка конфиденциальных данных

### Высокий (High)
- Частичный обход защиты
- DoS уязвимости
- Небезопасные значения по умолчанию

### Средний (Medium)
- Проблемы с безопасностью при особых условиях
- Утечка неконфиденциальной информации

### Низкий (Low)
- Теоретические уязвимости
- Проблемы, требующие маловероятных условий

## Гарантии безопасности

### Что мы гарантируем
1. **Открытость:** Весь код открыт для аудита
2. **Проверка:** Независимые криптографические обзоры
3. **Тестирование:** Регулярное тестирование на безопасность
4. **Обновления:** Своевременные исправления уязвимостей

### Что мы не гарантируем
1. **Защита от государственных АНБ:** Мы не утверждаем, что противостоим целевым атакам государственного уровня
2. **Неправильное использование:** Безопасность зависит от правильного использования
3. **Устаревшие версии:** Мы поддерживаем только последние стабильные версии

## Криптографические принципы

### Реализованные стандарты
- AES: FIPS 197, NIST SP 800-38A
- SHA-2: FIPS 180-4
- SHA-3: FIPS 202
- HMAC: RFC 2104
- GCM: NIST SP 800-38D
- PBKDF2: RFC 2898

### Рекомендации по использованию
1. **Ключи:** Используйте ключи длиной не менее 256 бит
2. **Режимы:** Предпочитайте аутентифицированное шифрование (GCM)
3. **Пароли:** Минимум 100,000 итераций для PBKDF2
4. **Случайность:** Используйте криптографически безопасный ГСЧ

## Аудит безопасности

### Внутренние проверки
- Ежеквартальный статический анализ
- Регулярное фаззинг-тестирование
- Тестирование на side-channel атаки

### Внешние аудиты
- Ежегодный независимый криптографический аудит
- Bug bounty программа (планируется)
- Публичные вызовы на взлом

## Управление зависимостями

### Мониторинг уязвимостей
- Еженедельное сканирование зависимостей
- Автоматические обновления патчей безопасности
- CVE отслеживание

### Критические зависимости
- Python стандартная библиотека
- Опционально: OpenSSL для совместимости

## Ответственность пользователей

### Рекомендации
1. **Обновления:** Всегда используйте последнюю версию
2. **Конфигурация:** Следуйте рекомендациям по безопасности
3. **Мониторинг:** Подпишитесь на уведомления о безопасности

### Что избегать
1. **Самодельная криптография:** Не изменяйте алгоритмы
2. **Устаревшие режимы:** Избегайте ECB, неаутентифицированных режимов
3. **Короткие ключи:** Используйте рекомендуемые длины ключей

## Контакты безопасности

### Основные контакты
- **Ответственный за безопасность:** security@example.com
- **Экстренные контакты:** Указаны в PGP ключе репозитория

### PGP ключ
```asciiarmor
-----BEGIN PGP PUBLIC KEY BLOCK-----
[Ключ для шифрования сообщений безопасности]
-----END PGP PUBLIC KEY BLOCK-----
История исправлений
Все исправления безопасности документируются в:

CHANGELOG.md

GitHub Releases

Security Advisories (GitHub)

Последнее обновление: Январь 2024



### **8. Создание структуры тестов**

Создайте следующие директории и базовые тестовые файлы:


# Создаем структуру тестов
mkdir -p tests/unit tests/integration tests/vectors

# Базовые юнит-тесты
touch tests/unit/test_aes.py
touch tests/unit/test_modes.py
touch tests/unit/test_hash.py
touch tests/unit/test_mac.py
touch tests/unit/test_kdf.py

# Интеграционные тесты
touch tests/integration/test_cli.py
touch tests/integration/test_file_io.py

# Пример test_aes.py
cat > tests/unit/test_aes.py << 'EOF'
import pytest
from cryptocore.aes import encrypt_block, decrypt_block

class TestAES:
    def test_encrypt_decrypt_block(self):
        """Test basic AES block encryption and decryption"""
        key = b'0' * 16
        plaintext = b'hello world!!!!!!'
        
        ciphertext = encrypt_block(key, plaintext)
        assert len(ciphertext) == 16
        assert ciphertext != plaintext
        
        decrypted = decrypt_block(key, ciphertext)
        assert decrypted == plaintext
    
    def test_invalid_key_length(self):
        """Test encryption with invalid key length"""
        key = b'0' * 15  # Invalid length
        plaintext = b'hello world!!!!!!'
        
        with pytest.raises(ValueError):
            encrypt_block(key, plaintext)
    
    def test_invalid_plaintext_length(self):
        """Test encryption with invalid plaintext length"""
        key = b'0' * 16
        plaintext = b'short'  # Invalid length
        
        with pytest.raises(ValueError):
            encrypt_block(key, plaintext)


# Пример test_cli.py
cat > tests/integration/test_cli.py << 'EOF'
import subprocess
import tempfile
import os

def test_cli_encrypt_decrypt():
    """Test CLI encryption and decryption round-trip"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Test data for encryption")
        input_file = f.name
    
    encrypted_file = input_file + '.enc'
    decrypted_file = input_file + '.dec'
    
    key = "00112233445566778899aabbccddeeff"
    
    try:
        # Encrypt
        result = subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'cbc', '--encrypt',
            '--key', key,
            '--input', input_file,
            '--output', encrypted_file
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Encryption failed: {result.stderr}"
        assert os.path.exists(encrypted_file)
        
        # Decrypt
        result = subprocess.run([
            'cryptocore', '--algorithm', 'aes', '--mode', 'cbc', '--decrypt',
            '--key', key,
            '--input', encrypted_file,
            '--output', decrypted_file
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Decryption failed: {result.stderr}"
        assert os.path.exists(decrypted_file)
        
        # Compare
        with open(input_file, 'rb') as f:
            original = f.read()
        with open(decrypted_file, 'rb') as f:
            decrypted = f.read()
        
        assert original == decrypted
        
    finally:
        # Cleanup
        for file in [input_file, encrypted_file, decrypted_file]:
            if os.path.exists(file):
                os.unlink(file)
1
