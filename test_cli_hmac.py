import unittest
import os
import tempfile
import subprocess
import sys

class TestCLIHMAC(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Удаляем временные файлы
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)
    
    def run_command(self, cmd):
      
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result
    
    def test_hmac_generation(self):
        
        # Создаем тестовый файл
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        cmd = f"python -m src.cli dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input {test_file}"
        result = self.run_command(cmd)
        
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        
        # Проверяем формат вывода: HMAC_VALUE FILENAME
        parts = output.split()
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[1], test_file)
        
        # Проверяем длину HMAC
        self.assertEqual(len(parts[0]), 64)  # 64 hex символа
    
    def test_hmac_verification_success(self):
 
        # Создаем тестовый файл
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        key = "00112233445566778899aabbccddeeff"
        
        # Генерируем HMAC
        cmd1 = f"python -m src.cli dgst --algorithm sha256 --hmac --key {key} --input {test_file}"
        result1 = self.run_command(cmd1)
        
        # Сохраняем HMAC в файл
        hmac_file = os.path.join(self.test_dir, "hmac.txt")
        with open(hmac_file, 'w') as f:
            f.write(result1.stdout)
        
        # Верифицируем
        cmd2 = f"python -m src.cli dgst --algorithm sha256 --hmac --key {key} --input {test_file} --verify {hmac_file}"
        result2 = self.run_command(cmd2)
        
        self.assertEqual(result2.returncode, 0)
        self.assertIn("[OK] HMAC verification successful", result2.stdout)
    
    def test_hmac_verification_failure(self):
       
        # Создаем тестовый файл
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Original content")
        
        key = "00112233445566778899aabbccddeeff"
        
        # Генерируем HMAC
        cmd1 = f"python -m src.cli dgst --algorithm sha256 --hmac --key {key} --input {test_file}"
        result1 = self.run_command(cmd1)
        
        # Сохраняем HMAC в файл
        hmac_file = os.path.join(self.test_dir, "hmac.txt")
        with open(hmac_file, 'w') as f:
            f.write(result1.stdout)
        
        # Изменяем файл
        with open(test_file, 'w') as f:
            f.write("Modified content")
        
        # Пытаемся верифицировать с измененным файлом
        cmd2 = f"python -m src.cli dgst --algorithm sha256 --hmac --key {key} --input {test_file} --verify {hmac_file}"
        result2 = self.run_command(cmd2)
        
        self.assertNotEqual(result2.returncode, 0)
        self.assertIn("[ERROR] HMAC verification failed", result2.stdout)
    
    def test_key_required_with_hmac(self):
     
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        cmd = f"python -m src.cli dgst --algorithm sha256 --hmac --input {test_file}"
        result = self.run_command(cmd)
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--key is required when using --hmac", result.stderr)

if __name__ == '__main__':
    unittest.main()
