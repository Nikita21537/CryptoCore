from abc import ABC, abstractmethod

class HashInterface(ABC):
    @abstractmethod
    def update(self, data):
        pass
    
    @abstractmethod
    def digest(self):
        pass
    
    @abstractmethod
    def hexdigest(self):
        pass
