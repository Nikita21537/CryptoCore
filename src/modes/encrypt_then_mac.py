from ..mac import HMAC
from .base import CipherMode


class EncryptThenMAC:


    def __init__(self, cipher_mode: str, key: bytes, iv: bytes = None):
        # Derive two keys from master key using HKDF-like approach
        self.enc_key = key[:16]  # First 16 bytes for encryption
        self.mac_key = key[16:] if len(key) >= 32 else self._derive_mac_key(key)

        # Create cipher instance
        from . import create_mode
        self.cipher = create_mode(cipher_mode, self.enc_key, iv)

        # Create MAC instance
        self.hmac = HMAC(self.mac_key, 'sha256')

    def _derive_mac_key(self, key: bytes) -> bytes:

        # Simple KDF: HMAC(key, "MAC") truncated to 16 bytes
        from src.cryptocore.hash import SHA256
        h = SHA256()
        h.update(key + b"MAC")
        return h.digest()[:16]

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:

        # Encrypt
        ciphertext = self.cipher.encrypt(plaintext)

        # Compute MAC over ciphertext + AAD
        mac_data = ciphertext + aad
        tag = self.hmac.compute(mac_data)

        # Return: ciphertext + tag
        return ciphertext + tag

    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:

        if len(data) < 32:  # Minimum: 0 ciphertext + 32 byte HMAC
            raise ValueError("Data too short")

        # Split ciphertext and tag
        ciphertext = data[:-32]
        tag = data[-32:]

        # Verify MAC
        mac_data = ciphertext + aad
        if not self.hmac.verify(mac_data, tag):
            raise AuthenticationError("Encrypt-then-MAC authentication failed")

        # Decrypt
        plaintext = self.cipher.decrypt(ciphertext)

        return plaintext


class AEADMode(CipherMode):


    def __init__(self, key: bytes, iv: bytes = None, mode_name: str = ""):
        super().__init__(key, iv, mode_name)
        self._aad = b""

    def set_aad(self, aad: bytes):

        self._aad = aad

    @abstractmethod
    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes, aad: bytes = b"") -> bytes:
        pass