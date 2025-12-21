from src.csprng import generate_random_bytes
from src.modes.ctr import CTR
from src.mac.hmac import HMAC


class EncryptThenMAC:
    """Реализация парадигмы Encrypt-then-MAC"""

    def __init__(self, key):
        if len(key) < 32:
            raise ValueError("Key must be at least 32 bytes for Encrypt-then-MAC")

        # Разделение ключа
        self.enc_key = key[:16]
        self.mac_key = key[16:32]

        # Инициализация шифрования и MAC
        self.encryptor = CTR(self.enc_key)
        self.hmac = HMAC(self.mac_key, 'sha256')

    def encrypt(self, plaintext, iv=None, aad=b""):
        """Шифрование с последующим MAC"""
        if iv is None:
            iv = generate_random_bytes(16)

        # Шифрование
        ciphertext = self.encryptor.encrypt(plaintext, iv=iv)

        # Вычисление MAC над ciphertext и AAD
        mac_data = ciphertext + aad
        tag = self.hmac.compute(mac_data)

        return {
            'iv': iv,
            'ciphertext': ciphertext,
            'tag': tag
        }

    def decrypt(self, iv, ciphertext, tag, aad=b""):
        """Дешифрование с проверкой MAC"""
        # Сначала проверяем MAC
        mac_data = ciphertext + aad
        expected_tag = self.hmac.compute(mac_data)

        if tag != expected_tag:
            raise ValueError("MAC verification failed")

        # Затем дешифруем
        plaintext = self.encryptor.decrypt(ciphertext, iv=iv)

        return plaintext
