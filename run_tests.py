


import unittest
import sys
import os
import argparse
from pathlib import Path

def discover_tests(test_dir, pattern='test_*.py'):

    loader = unittest.TestLoader()
    return loader.discover(test_dir, pattern=pattern)

def run_tests(verbosity=2, test_type='all'):
    
    # Добавляем src в PYTHONPATH
    src_dir = Path(__file__).parent.parent / 'src'
    sys.path.insert(0, str(src_dir))
    
    # Создаем тестовый набор
    suite = unittest.TestSuite()
    
    # Определяем, какие тесты запускать
    if test_type in ['all', 'unit']:
        suite.addTests(discover_tests('tests/unit'))
    
    if test_type in ['all', 'integration']:
        suite.addTests(discover_tests('tests/integration'))
    
    if test_type in ['all', 'vectors']:
        # Тестовые векторы могут быть не unittest-тестами
        # Запускаем их отдельно если нужно
        pass
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_performance_tests():
   
    print("Запуск тестов производительности...")
    
    try:
        # Импортируем здесь, чтобы не ломать обычные тесты
        import timeit
        from cryptocore.aes import encrypt_block
        
        # Тест скорости AES
        key = b'0' * 16
        plaintext = b'1' * 16
        
        def aes_benchmark():
            for _ in range(1000):
                encrypt_block(key, plaintext)
        
        time = timeit.timeit(aes_benchmark, number=10)
        print(f"AES encrypt_block: {time:.3f} секунд на 10,000 операций")
        
        return True
    except Exception as e:
        print(f"Ошибка в тестах производительности: {e}")
        return False

def run_memory_tests():
   
    print("Запуск тестов памяти...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Тест с большим файлом
        from cryptocore.aes import encrypt_block
        
        # Симулируем обработку больших данных
        key = b'0' * 16
        data = b'x' * 1000000  # 1MB
        
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            if len(chunk) == 16:
                encrypt_block(key, chunk)
        
        mem_after = process.memory_info().rss / 1024 / 1024
        
        print(f"Память до: {mem_before:.1f} MB")
        print(f"Память после: {mem_after:.1f} MB")
        print(f"Разница: {mem_after - mem_before:.1f} MB")
        
        # Проверяем, что нет утечек памяти
        if mem_after - mem_before > 10:  # Больше 10MB разницы
            print("ВНИМАНИЕ: Возможная утечка памяти")
            return False
        
        return True
    except ImportError:
        print("psutil не установлен, пропускаем тесты памяти")
        print("Установите: pip install psutil")
        return True
    except Exception as e:
        print(f"Ошибка в тестах памяти: {e}")
        return False

def main():
  
    parser = argparse.ArgumentParser(description='Запуск тестов CryptoCore')
    parser.add_argument('--type', choices=['all', 'unit', 'integration', 'performance', 'memory'],
                       default='all', help='Тип тестов для запуска')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                       help='Уровень детализации (0-2)')
    parser.add_argument('--list', action='store_true',
                       help='Показать все доступные тесты')
    
    args = parser.parse_args()
    
    # Устанавливаем уровень детализации
    verbosity = 1
    if args.verbose == 1:
        verbosity = 2
    elif args.verbose >= 2:
        verbosity = 3
    
    # Меняем рабочую директорию на корень проекта
    os.chdir(Path(__file__).parent.parent)
    
    if args.list:
        # Показываем все тесты
        print("Доступные тесты:")
        print("1. Юнит-тесты (--type unit)")
        print("   tests/unit/test_aes.py")
        print("   tests/unit/test_modes.py")
        print("   tests/unit/test_hash.py")
        print("   tests/unit/test_mac.py")
        print("   tests/unit/test_kdf.py")
        print()
        print("2. Интеграционные тесты (--type integration)")
        print("   tests/integration/test_cli.py")
        print("   tests/integration/test_file_io.py")
        print()
        print("3. Тесты производительности (--type performance)")
        print("4. Тесты памяти (--type memory)")
        return 0
    
    print("=" * 60)
    print("Запуск тестов CryptoCore")
    print("=" * 60)
    
    success = True
    
    try:
        if args.type in ['all', 'unit', 'integration']:
            print(f"\nЗапуск {args.type} тестов...")
            success = run_tests(verbosity, args.type)
        
        if args.type in ['all', 'performance']:
            print(f"\nЗапуск тестов производительности...")
            perf_success = run_performance_tests()
            success = success and perf_success
        
        if args.type in ['all', 'memory']:
            print(f"\nЗапуск тестов памяти...")
            mem_success = run_memory_tests()
            success = success and mem_success
        
    except KeyboardInterrupt:
        print("\nТесты прерваны пользователем")
        return 1
    except Exception as e:
        print(f"\nОшибка при запуске тестов: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Все тесты прошли успешно!")
        return 0
    else:
        print("❌ Некоторые тесты не прошли")
        return 1

if __name__ == '__main__':
    sys.exit(main())
