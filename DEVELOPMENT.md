### **3. `docs/DEVELOPMENT.md`**

```markdown
# Руководство разработчика CryptoCore

## Настройка среды разработки

### Требования
- Python 3.8 или выше
- Git
- pip

### Установка зависимостей разработки
```bash
git clone https://github.com/Nikita21537/CryptoCore.git
cd CryptoCore
pip install -e ".[dev]"
Зависимости разработки (setup.py/extras_require)
python
extras_require={
    'dev': [
        'pytest>=7.0',
        'pytest-cov>=4.0',
        'mypy>=1.0',
        'flake8>=6.0',
        'black>=23.0',
        'isort>=5.0',
    ]
}
Структура проекта
text
CryptoCore/
├── src/cryptocore/          # Исходный код библиотеки
│   ├── __init__.py
│   ├── aes.py              # Реализация AES
│   ├── modes.py            # Режимы шифрования
│   ├── hash.py             # Хеш-функции
│   ├── mac.py              # MAC функции
│   ├── kdf.py              # Key Derivation Functions
│   ├── csprng.py           # CSPRNG
│   └── cli.py              # CLI интерфейс
├── tests/                  # Тесты
├── docs/                   # Документация
└── scripts/               # Вспомогательные скрипты
Процесс разработки
1. Создание новой функциональности
bash
# 1. Создайте ветку для новой функции
git checkout -b feature/new-algorithm

# 2. Реализуйте функциональность с тестами
# 3. Проверьте код
pytest
mypy src/
flake8 src/
black src/

# 4. Создайте Pull Request
2. Коммиты
Используйте Conventional Commits:

feat: Новая функциональность

fix: Исправление ошибки

docs: Изменения в документации

test: Изменения в тестах

refactor: Рефакторинг кода

chore: Обновление зависимостей, настройки

Пример:

bash
git commit -m "feat: add ChaCha20 stream cipher implementation"
git commit -m "fix: correct IV handling in CBC mode"
Тестирование
Запуск тестов
bash
# Все тесты
python -m pytest tests/

# Только юнит-тесты
python -m pytest tests/unit/

# С покрытием кода
python -m pytest --cov=src tests/

# Конкретный тестовый файл
python -m pytest tests/unit/test_aes.py

# Тесты с детальным выводом
python -m pytest -v tests/
Добавление новых тестов
Создайте файл в соответствующей директории:

tests/unit/ для юнит-тестов

tests/integration/ для интеграционных тестов

Используйте шаблон:

python
import pytest
from cryptocore.aes import encrypt_block

def test_encrypt_block_valid():
    """Test AES block encryption with valid input"""
    key = b'0' * 16
    plaintext = b'hello world!!!!!!'
    ciphertext = encrypt_block(key, plaintext)
    assert len(ciphertext) == 16
    assert ciphertext != plaintext

def test_encrypt_block_invalid_key():
    """Test AES block encryption with invalid key length"""
    key = b'0' * 15  # Invalid length
    plaintext = b'hello world!!!!!!'
    with pytest.raises(ValueError):
        encrypt_block(key, plaintext)
Статический анализ кода
Типизация (mypy)
bash
mypy src/ --strict
Линтинг (flake8)
bash
flake8 src/
Форматирование (black)
bash
black src/ tests/
Сортировка импортов (isort)
bash
isort src/ tests/
Сборка и распространение
Сборка пакета
bash
python -m build
Тестирование пакета
bash
# Установка из собранного пакета
pip install dist/cryptocore-*.whl

# Проверка импортов
python -c "import cryptocore; print(cryptocore.__version__)"
Публикация на PyPI (для maintainers)
bash
# Требуется доступ к PyPI
python -m twine upload dist/*
Тестовые векторы
Добавление тестовых векторов
Разместите файлы в tests/vectors/

Формат: JSON, CSV или plain text

Пример: tests/vectors/aes_gcm_nist.json

Использование тестовых векторов
python
import json
from pathlib import Path

def load_test_vectors(filename):
    """Load test vectors from file"""
    vector_path = Path(__file__).parent / 'vectors' / filename
    with open(vector_path) as f:
        return json.load(f)
Производительность
Бенчмарки
bash
# Запуск бенчмарков
python scripts/benchmark.py

# Профилирование
python -m cProfile -o profile.stats scripts/profile.py
Оптимизация критических участков
Используйте timeit для измерения

Профилируйте с помощью cProfile

Рассмотрите использование Cython для горячих точек

Безопасность
Аудит безопасности
Статический анализ: bandit, safety

Динамический анализ: fuzzing с помощью AFL++

Проверка уязвимостей: pip-audit

Инструменты безопасности
bash
# Поиск уязвимостей в коде
bandit -r src/

# Проверка зависимостей на уязвимости
pip-audit

# Fuzzing тесты
python -m pytest tests/fuzz/ -x
Документация
Генерация документации
bash
# API документация из docstrings
pdoc --html src/cryptocore --output-dir docs/api

# Обновление README
python scripts/update_readme.py
Живые примеры
Размещайте исполняемые примеры в docs/examples/:

python
# docs/examples/encryption_demo.py
"""
Пример шифрования файла с использованием CryptoCore
"""
from cryptocore import aes, modes
import os

# Генерация ключа
key = os.urandom(32)
iv = os.urandom(16)

# Шифрование
plaintext = b"Secret message"
ciphertext = modes.cbc_encrypt(key, iv, plaintext)
Контрибуция
Pull Request процесс
Форкните репозиторий

Создайте feature branch

Реализуйте изменения с тестами

Обновите документацию

Пройдите все проверки CI

Создайте PR с описанием изменений

Code Review Guidelines
Проверяйте безопасность криптографических реализаций

Убедитесь в наличии тестов

Проверьте покрытие кода

Убедитесь в обновлении документации

CI/CD
