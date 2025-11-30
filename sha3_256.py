import hashlib

class SHA3_256:
    def __init__(self):
        self._hash = hashlib.sha3_256()
    
    def update(self, data):
        """Update hash with data"""
        self._hash.update(data)
    
    def digest(self):
        """Return final hash digest"""
        return self._hash.digest()
    
    def hexdigest(self):
        """Return final hash as hexadecimal string"""
        return self._hash.hexdigest()
    
    def hash(self, data):
        """Convenience method to hash entire data at once"""
        self.update(data)
        return self.hexdigest()
