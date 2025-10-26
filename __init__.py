
import sys
import os

# Добавление пути для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_parser import parse_arguments
from file_io import read_file, write_file
from modes.ecb import encrypt_ecb, decrypt_ecb

def main():
    """Основная функция приложения"""
    try:
        # Парсинг аргументов
        args = parse_arguments()
        
        # Чтение входного файла
        input_data = read_file(args.input)
        
        # Преобразование ключа из hex в bytes
        key = bytes.fromhex(args.key)
        
        # Выполнение операции
        if args.encrypt:
            output_data = encrypt_ecb(input_data, key)
            operation = "шифрования"
        else:
            output_data = decrypt_ecb(input_data, key)
            operation = "дешифрования"
        
        # Запись выходного файла
        write_file(args.output, output_data)
        
        print(f"Операция {operation} завершена успешно")
        print(f"Входной файл: {args.input}")
        print(f"Выходной файл: {args.output}")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
