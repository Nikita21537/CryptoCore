import hashlib

class SHA3_256:
    def __init__(self):
        self._hash = hashlib.sha3_256()
    
    def update(self, data):
      
        self._hash.update(data)
    
    def digest(self):
       
        return self._hash.digest()
    
    def hexdigest(self):
        
        return self._hash.hexdigest()
    
    def hash(self, data):
        
        self.update(data)
        return self.hexdigest()
