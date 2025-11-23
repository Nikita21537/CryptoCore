import sys
from src.cli_parser import parse_args
from src.file_io import read_file, write_file, handle_file_error
from src.crypto_core import CryptoCore

def main():
    try:
        args = parse_args()
        
        # Чтение входного файла
        input_data = read_file(args.input)
        
        # Подготовка ключа
        key = bytes.fromhex(args.key)
        
        # Создание криптографического ядра
        crypto = CryptoCore(args.algorithm, args.mode, key)
        
        # Выполнение операции
        if args.encrypt:
            output_data = crypto.encrypt(input_data)
        else:
            # Для дешифрования обрабатываем IV
            iv = None
            if args.iv:
                iv = bytes.fromhex(args.iv)
            elif args.mode in ['cbc', 'cfb', 'ofb', 'ctr']:
                # Если IV не предоставлен, читаем из файла
                if len(input_data) < 16:
                    raise ValueError("Input file too short to contain IV")
                iv = input_data[:16]
                input_data = input_data[16:]
            
            output_data = crypto.decrypt(input_data, iv)
        
        # Запись выходного файла
        write_file(args.output, output_data)
        
        print(f"Operation completed successfully: {args.input} -> {args.output}")
        
    except Exception as e:
        handle_file_error(e)

if __name__ == "__main__":
    main()
