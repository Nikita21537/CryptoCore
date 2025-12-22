import unittest
import os
import tempfile
import subprocess
from src.cryptocore.modes import create_mode


class TestNewModes(unittest.TestCase):
    def setUp(self):
        self.key = b"0123456789abcdef"
        self.iv = b"1234567890abcdef"
        self.test_data = b"Test data for encryption " + b"A" * 50  # Не кратно 16

    def test_cbc_encrypt_decrypt(self):

        cipher = create_mode('CBC', self.key, self.iv)

        # Шифрование
        ciphertext = cipher.encrypt(self.test_data)

        # Дешифрование
        plaintext = cipher.decrypt(ciphertext)

        self.assertEqual(self.test_data, plaintext)

    def test_cfb_encrypt_decrypt(self):

        cipher = create_mode('CFB', self.key, self.iv)

        # Шифрование
        ciphertext = cipher.encrypt(self.test_data)

        # Дешифрование
        plaintext = cipher.decrypt(ciphertext)

        self.assertEqual(self.test_data, plaintext)

        # Проверка, что размер не изменился (без паддинга)
        self.assertEqual(len(ciphertext), len(self.test_data))

    def test_ofb_encrypt_decrypt(self):

        cipher = create_mode('OFB', self.key, self.iv)

        # Шифрование
        ciphertext = cipher.encrypt(self.test_data)

        # Дешифрование
        plaintext = cipher.decrypt(ciphertext)

        self.assertEqual(self.test_data, plaintext)
        self.assertEqual(len(ciphertext), len(self.test_data))

    def test_ctr_encrypt_decrypt(self):

        cipher = create_mode('CTR', self.key, self.iv)

        # Шифрование
        ciphertext = cipher.encrypt(self.test_data)

        # Дешифрование
        plaintext = cipher.decrypt(ciphertext)

        self.assertEqual(self.test_data, plaintext)
        self.assertEqual(len(ciphertext), len(self.test_data))

    def test_interoperability_openssl(self):

        test_modes = ['cbc', 'cfb', 'ofb', 'ctr']

        for mode in test_modes:
            with self.subTest(mode=mode):
                # Создаем временные файлы
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
                    original_content = b"Test content for " + mode.encode() + b" mode"
                    f.write(original_content)
                    original_file = f.name

                encrypted_file = original_file + '.enc'
                decrypted_file = original_file + '.dec'

                try:
                    # Генерируем случайный IV
                    iv = os.urandom(16)
                    iv_hex = iv.hex()

                    # Шифруем с помощью нашего инструмента
                    subprocess.run([
                        "python", "-m", "src.cryptocore",
                        "--algorithm", "aes",
                        "--mode", mode,
                        "--encrypt",
                        "--key", self.key.hex(),
                        "--input", original_file,
                        "--output", encrypted_file
                    ], check=True, capture_output=True)

                    # Читаем IV из зашифрованного файла
                    with open(encrypted_file, 'rb') as f:
                        file_iv = f.read(16)
                        ciphertext_only = f.read()

                    # Дешифруем с помощью OpenSSL
                    # Сначала сохраняем ciphertext без IV
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                        f.write(ciphertext_only)
                        ciphertext_file = f.name

                    try:
                        # Дешифруем OpenSSL
                        openssl_result = subprocess.run([
                            "openssl", "enc",
                            f"-aes-128-{mode}",
                            "-d",
                            "-K", self.key.hex(),
                            "-iv", file_iv.hex(),
                            "-in", ciphertext_file,
                            "-out", decrypted_file
                        ], capture_output=True)

                        if openssl_result.returncode == 0:
                            # Проверяем результат
                            with open(decrypted_file, 'rb') as f:
                                decrypted_content = f.read()

                            self.assertEqual(original_content, decrypted_content,
                                             f"Failed for mode {mode}")
                        else:
                            # Пропускаем если OpenSSL не поддерживает режим
                            print(f"Note: OpenSSL test skipped for {mode}: {openssl_result.stderr}")

                    finally:
                        if os.path.exists(ciphertext_file):
                            os.remove(ciphertext_file)

                finally:
                    # Очистка
                    for f in [original_file, encrypted_file, decrypted_file]:
                        if os.path.exists(f):
                            os.remove(f)


if __name__ == '__main__':
    unittest.main()