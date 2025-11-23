from abc import ABC, abstractmethod

class ModeInterface(ABC):
    @abstractmethod
    def encrypt(self, plaintext):
        pass

    @abstractmethod
    def decrypt(self, ciphertext):
        pass
