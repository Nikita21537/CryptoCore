import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .aes import *
from .modes import *
from .hash import sha256, sha256_hex, sha3_256, sha3_256_hex
from .mac import hmac_sha256, hmac_sha256_hex, hmac_sha3_256, hmac_sha3_256_hex
from .kdf import pbkdf2_hmac_sha256
from .csprng import generate_random_bytes


class CryptoCoreCLI:
  
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Создание парсера аргументов"""
        parser = argparse.ArgumentParser(
            description='CryptoCore - Cryptographic Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  Шифрование файла:
    cryptocore --algorithm aes --mode cbc --encrypt --key KEY --input file.txt --output file.enc
  
  Дешифрование файла:
    cryptocore --algorithm aes --mode cbc --decrypt --key KEY --input file.enc --output file.txt
  
  Хеширование SHA3-256:
    cryptocore --algorithm sha3_256 --input file.txt
  
  HMAC-SHA3-256:
    cryptocore --algorithm hmac --hash sha3_256 --key SECRET --input file.txt
  
  Деривация ключа:
    cryptocore derive --password "mypass" --salt "somesalt" --iterations 100000
            """
        )
        
        # Основные аргументы
        parser.add_argument('--algorithm', '-a', 
                          choices=['aes', 'sha256', 'sha3_256', 'hmac'],
                          help='Алгоритм для использования')
        
        parser.add_argument('--mode', '-m',
                          choices=['ecb', 'cbc', 'cfb', 'ofb', 'ctr', 'gcm'],
                          default='cbc',
                          help='Режим шифрования (по умолчанию: cbc)')
        
        parser.add_argument('--encrypt', '-e', action='store_true',
                          help='Режим шифрования')
        
        parser.add_argument('--decrypt', '-d', action='store_true',
                          help='Режим дешифрования')
        
        parser.add_argument('--key', '-k',
                          help='Ключ в hex-строке или файл с ключом')
        
        parser.add_argument('--input', '-i', required=True,
                          help='Входной файл')
        
        parser.add_argument('--output', '-o',
                          help='Выходной файл (опционально)')
        
        parser.add_argument('--iv',
                          help='Вектор инициализации в hex-строке')
        
        parser.add_argument('--aad',
                          help='Дополнительные аутентифицированные данные (GCM)')
        
        # Для HMAC
        parser.add_argument('--hash',
                          choices=['sha256', 'sha3_256'],
                          default='sha256',
                          help='Хеш-функция для HMAC (по умолчанию: sha256)')
        
        parser.add_argument('--verify',
                          help='HMAC для проверки в hex-строке')
        
        # Подкоманда derive
        subparsers = parser.add_subparsers(dest='command', help='Команды')
        
        derive_parser = subparsers.add_parser('derive', 
                                            help='Деривация ключа из пароля')
        derive_parser.add_argument('--password', '-p', required=True,
                                 help='Пароль для деривации')
        derive_parser.add_argument('--salt', '-s',
                                 help='Соль в hex-строке')
        derive_parser.add_argument('--iterations', '-i', type=int, default=100000,
                                 help='Количество итераций (по умолчанию: 100000)')
        derive_parser.add_argument('--length', '-l', type=int, default=32,
                                 help='Длина ключа в байтах (по умолчанию: 32)')
        derive_parser.add_argument('--algorithm', '-a', 
                                 choices=['pbkdf2'], default='pbkdf2',
                                 help='Алгоритм KDF (по умолчанию: pbkdf2)')
        derive_parser.add_argument('--output', '-o',
                                 help='Файл для сохранения ключа')
        
        return parser
    
    def _read_key(self, key_arg: str) -> bytes:
      
        # Если это файл
        if os.path.exists(key_arg):
            with open(key_arg, 'rb') as f:
                return f.read().strip()
        
        # Если это hex-строка
        try:
            if len(key_arg) % 2 == 0:
                return bytes.fromhex(key_arg)
        except ValueError:
            pass
        
        # Если это обычная строка
        return key_arg.encode('utf-8')
    
    def _read_file_or_stdin(self, input_arg: str) -> bytes:
        
        if input_arg == '-':
            return sys.stdin.buffer.read()
        else:
            with open(input_arg, 'rb') as f:
                return f.read()
    
    def _write_output(self, data: bytes, output_arg: Optional[str]):
      
        if output_arg:
            with open(output_arg, 'wb') as f:
                f.write(data)
        else:
            sys.stdout.buffer.write(data)
    
    def handle_hash(self, args):
       
        data = self._read_file_or_stdin(args.input)
        
        if args.algorithm == 'sha256':
            result = sha256_hex(data)
        elif args.algorithm == 'sha3_256':
            result = sha3_256_hex(data)
        else:
            raise ValueError(f"Unsupported algorithm: {args.algorithm}")
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result + '\n')
        else:
            print(result)
    
    def handle_hmac(self, args):
     
        if not args.key:
            raise ValueError("Key is required for HMAC")
        
        data = self._read_file_or_stdin(args.input)
        key = self._read_key(args.key)
        
        if args.hash == 'sha256':
            hmac_func = hmac_sha256_hex
        elif args.hash == 'sha3_256':
            hmac_func = hmac_sha3_256_hex
        else:
            raise ValueError(f"Unsupported hash: {args.hash}")
        
        hmac_value = hmac_func(key, data)
        
        if args.verify:
            if hmac_value == args.verify:
                print("✓ HMAC verification successful")
                return 0
            else:
                print("✗ HMAC verification failed")
                print(f"  Expected: {args.verify}")
                print(f"  Got:      {hmac_value}")
                return 1
        else:
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(hmac_value + '\n')
            else:
                print(hmac_value)
            return 0
    
    def handle_encryption(self, args):
       
        if not args.key:
            raise ValueError("Key is required for encryption/decryption")
        
        data = self._read_file_or_stdin(args.input)
        key = self._read_key(args.key)
        
        # Генерация IV если не указан
        iv = None
        if args.iv:
            iv = bytes.fromhex(args.iv)
        elif args.mode != 'ecb':
            iv = generate_random_bytes(16)
        
        if args.encrypt:
            if args.mode == 'cbc':
                ciphertext = cbc_encrypt(key, iv, data)
            elif args.mode == 'gcm':
                aad = args.aad.encode('utf-8') if args.aad else b''
                ciphertext, tag = gcm_encrypt(key, data, aad)
                # Сохраняем tag вместе с данными
                data_to_write = ciphertext + tag
            else:
                raise ValueError(f"Mode {args.mode} not yet implemented")
            
            # Для GCM уже обработано
            if args.mode != 'gcm':
                data_to_write = ciphertext
            
            self._write_output(data_to_write, args.output)
            
            # Выводим IV если нужно
            if iv and not args.output:
                print(f"IV (hex): {iv.hex()}")
        
        elif args.decrypt:
            if args.mode == 'cbc':
                plaintext = cbc_decrypt(key, iv, data)
            elif args.mode == 'gcm':
                # Разделяем ciphertext и tag
                ciphertext = data[:-16]
                tag = data[-16:]
                aad = args.aad.encode('utf-8') if args.aad else b''
                plaintext = gcm_decrypt(key, ciphertext, tag, aad)
            else:
                raise ValueError(f"Mode {args.mode} not yet implemented")
            
            self._write_output(plaintext, args.output)
    
    def handle_derive(self, args):
    
        password = args.password
        salt = args.salt
        
        if salt:
            if len(salt) % 2 == 0 and all(c in '0123456789abcdefABCDEF' for c in salt):
                salt_bytes = bytes.fromhex(salt)
            else:
                salt_bytes = salt.encode('utf-8')
        else:
            # Генерация случайной соли
            salt_bytes = generate_random_bytes(16)
        
        # Деривация ключа
        if args.algorithm == 'pbkdf2':
            key = pbkdf2_hmac_sha256(
                password.encode('utf-8'),
                salt_bytes,
                args.iterations,
                args.length
            )
        else:
            raise ValueError(f"Unsupported KDF algorithm: {args.algorithm}")
        
        # Вывод результата
        if args.output:
            with open(args.output, 'wb') as f:
                f.write(key)
            print(f"Key saved to {args.output}")
            print(f"Salt (hex): {salt_bytes.hex()}")
        else:
            # Формат: KEY_HEX:SALT_HEX
            print(f"{key.hex()}:{salt_bytes.hex()}")
    
    def run(self):
      
        args = self.parser.parse_args()
        
        try:
            if args.command == 'derive':
                return self.handle_derive(args)
            
            if args.algorithm in ['sha256', 'sha3_256']:
                return self.handle_hash(args)
            
            elif args.algorithm == 'hmac':
                return self.handle_hmac(args)
            
            elif args.algorithm == 'aes':
                return self.handle_encryption(args)
            
            else:
                self.parser.print_help()
                return 1
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


def main():
    
    cli = CryptoCoreCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
