import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli_parser import parse_cli_args
from file_io import read_file, write_file
from modes.ecb import encrypt_ecb, decrypt_ecb

def main():
    """
    Основная функция приложения
    """
    try:
        # Парсинг аргументов командной строки
        args = parse_cli_args()
        
        # Преобразование ключа из hex в bytes
        key_bytes = bytes.fromhex(args.key)
        
        # Чтение входного файла
        input_data = read_file(args.input)
        
        # Выполнение операции
        if args.encrypt:
            if args.algorithm == "aes" and args.mode == "ecb":
                output_data = encrypt_ecb(input_data, key_bytes)
            else:
                print(f"Ошибка: Неподдерживаемая комбинация алгоритма и режима: {args.algorithm}-{args.mode}", file=sys.stderr)
                sys.exit(1)
        else:  # decrypt
            if args.algorithm == "aes" and args.mode == "ecb":
                output_data = decrypt_ecb(input_data, key_bytes)
            else:
                print(f"Ошибка: Неподдерживаемая комбинация алгоритма и режима: {args.algorithm}-{args.mode}", file=sys.stderr)
                sys.exit(1)
        
        # Запись выходного файла
        write_file(args.output, output_data)
        
        print(f"Операция завершена успешно!")
        print(f"Входной файл: {args.input}")
        print(f"Выходной файл: {args.output}")
        print(f"Размер входных данных: {len(input_data)} байт")
        print(f"Размер выходных данных: {len(output_data)} байт")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
