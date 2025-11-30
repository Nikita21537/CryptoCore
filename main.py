import sys
import os
from src.cli_parser import parse_args
from src.file_io import read_file, write_file, handle_file_error
from src.crypto_core import CryptoCore
from src.csprng import generate_random_bytes
from src.hash import get_hash_algorithm

def main():
    try:
        args = parse_args()
        
        if args.command == 'enc':
            _handle_encryption(args)
        elif args.command == 'dgst':
            _handle_hashing(args)
        else:
            print(f"Error: Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        handle_file_error(e)

def _handle_encryption(args):
    
    # Чтение входного файла
    input_data = read_file(args.input)
    
    # Подготовка ключа
    if args.key:
        key = bytes.fromhex(args.key)
    else:
        # Генерация случайного ключа для шифрования
        key = generate_random_bytes(16)
        key_hex = key.hex()
        print(f"[INFO] Generated random key: {key_hex}")
    
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

def _handle_hashing(args):
    
    
    if args.input == '-':
        
        input_data = sys.stdin.buffer.read()
        input_filename = '-'
    else:
        
        input_data = read_file(args.input)
        input_filename = args.input
    
    
    hash_algo = get_hash_algorithm(args.algorithm)
    
    
    chunk_size = 8192  # 8KB chunks
    if len(input_data) <= chunk_size:
        hash_algo.update(input_data)
    else:
        # Process large file in chunks
        for i in range(0, len(input_data), chunk_size):
            chunk = input_data[i:i + chunk_size]
            hash_algo.update(chunk)
    
    
    hash_result = hash_algo.hexdigest()
    
    
    output_line = f"{hash_result}  {input_filename}\n"
    
   
    if args.output:
        write_file(args.output, output_line.encode('utf-8'))
        print(f"Hash written to: {args.output}")
    else:
        print(output_line, end='')

if __name__ == "__main__":
    main()
