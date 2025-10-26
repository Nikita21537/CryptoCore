import argparse
import sys
import os

def parse_cli_args():
    """
    Парсинг аргументов командной строки
    """
    parser = argparse.ArgumentParser(
        description="CryptoCore - инструмент для криптографических операций",
        prog="cryptocore"
    )
    
    # Обязательные аргументы
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=["aes"],
        help="Алгоритм шифрования (поддерживается: aes)"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["ecb"],
        help="Режим работы (поддерживается: ecb)"
    )
    
    # Флаги шифрования/дешифрования (ровно один должен быть указан)
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument("--encrypt", action="store_true", help="Режим шифрования")
    operation_group.add_argument("--decrypt", action="store_true", help="Режим дешифрования")
    
    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help="Ключ в шестнадцатеричном формате (16 байт для AES-128)"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Путь к входному файлу"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help="Путь к выходному файлу (генерируется автоматически если не указан)"
    )
    
    args = parser.parse_args()
    
    # Валидация ключа
    if not validate_hex_key(args.key, 32):  # 32 hex символа = 16 байт
        print(f"Ошибка: Ключ должен быть 16-байтным значением в hex формате (32 символа)", file=sys.stderr)
        print(f"Получен ключ длиной {len(args.key)}: {args.key}", file=sys.stderr)
        sys.exit(1)
    
    # Проверка существования входного файла
    if not os.path.exists(args.input):
        print(f"Ошибка: Входной файл не существует: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Генерация имени выходного файла по умолчанию
    if not args.output:
        args.output = generate_default_output_filename(args.input, args.encrypt)
    
    return args

def validate_hex_key(key: str, expected_length: int) -> bool:
    """
    Валидация hex ключа
    """
    if len(key) != expected_length:
        return False
    
    try:
        int(key, 16)
        return True
    except ValueError:
        return False

def generate_default_output_filename(input_file: str, is_encrypt: bool) -> str:
    """
    Генерация имени выходного файла по умолчанию
    """
    if is_encrypt:
        return input_file + ".enc"
    else:
        if input_file.endswith('.enc'):
            return input_file + '.dec'
        else:
            return input_file + '.dec'
