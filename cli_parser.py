import argparse
import sys
import os
from src.hash.sha256 import SHA256
from src.mac.hmac import HMAC

def setup_parser():
    parser = argparse.ArgumentParser(
        description="CryptoCore - Cryptography Toolkit",
        prog="cryptocore"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Команда dgst
    dgst_parser = subparsers.add_parser('dgst', help='Message digest and MAC operations')
    
    # Группа для алгоритма
    algo_group = dgst_parser.add_argument_group('algorithm selection')
    algo_group.add_argument(
        '--algorithm', '-a',
        choices=['sha256'],
        default='sha256',
        help='Hash algorithm to use (default: sha256)'
    )
    
    # Группа для ввода
    input_group = dgst_parser.add_argument_group('input')
    input_group.add_argument(
        '--input', '-i',
        required=True,
        help='Input file path'
    )
    
    # Группа для вывода
    output_group = dgst_parser.add_argument_group('output')
    output_group.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    
    # Новые аргументы для HMAC
    mac_group = dgst_parser.add_argument_group('MAC options')
    mac_group.add_argument(
        '--hmac',
        action='store_true',
        help='Enable HMAC mode'
    )
    mac_group.add_argument(
        '--key', '-k',
        help='Key for HMAC (hexadecimal string)'
    )
    mac_group.add_argument(
        '--verify',
        metavar='FILE',
        help='Verify HMAC against value in FILE'
    )
    
    return parser

def dgst_command(args):
   
    # Проверка существования файла
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1
    
    # Если включен HMAC, проверяем наличие ключа
    if args.hmac:
        if not args.key:
            print("Error: --key is required when using --hmac", file=sys.stderr)
            return 1
        
        # Создаем объект HMAC
        try:
            hmac = HMAC(args.key, args.algorithm)
        except ValueError as e:
            print(f"Error: Invalid key - {e}", file=sys.stderr)
            return 1
        
        # Вычисляем HMAC
        hmac_value = hmac.compute_file(args.input)
        
        # Если требуется верификация
        if args.verify:
            try:
                with open(args.verify, 'r') as f:
                    expected_line = f.read().strip()
                
                # Парсим ожидаемое значение HMAC
                # Формат: HMAC_VALUE INPUT_FILE_PATH
                parts = expected_line.split()
                if parts:
                    expected_hmac = parts[0].strip()
                    
                    # Сравниваем
                    if hmac_value == expected_hmac:
                        print(f"[OK] HMAC verification successful")
                        return 0
                    else:
                        print(f"[ERROR] HMAC verification failed")
                        return 1
                else:
                    print(f"Error: Invalid HMAC file format", file=sys.stderr)
                    return 1
                    
            except FileNotFoundError:
                print(f"Error: HMAC file '{args.verify}' not found", file=sys.stderr)
                return 1
        
        # Формируем вывод в формате: HMAC_VALUE INPUT_FILE_PATH
        output = f"{hmac_value} {args.input}"
        
    else:
        # Обычное хэширование (из предыдущего спринта)
        hash_obj = SHA256()
        
        with open(args.input, 'rb') as f:
            while chunk := f.read(4096):
                hash_obj.update(chunk)
        
        output = f"{hash_obj.hexdigest()} {args.input}"
    
    # Записываем вывод
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output + '\n')
    else:
        print(output)
    
    return 0

def main():
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'dgst':
        return dgst_command(args)
    
    return 0

