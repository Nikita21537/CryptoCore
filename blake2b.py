

class BLAKE2b:
  
    
    # Константы для BLAKE2b
    IV = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]
    
    # Константы для перестановки
    SIGMA = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
        [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
        [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
        [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
        [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
        [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
        [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
        [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
        [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3]
    ]
    
    def __init__(self, data=b'', digest_size=64, key=b''):
    
        if digest_size < 1 or digest_size > 64:
            raise ValueError("digest_size must be between 1 and 64 bytes")
        
        if len(key) > 64:
            raise ValueError("key must be at most 64 bytes")
        
        self.digest_size = digest_size
        self.block_size = 128  # bytes
        self.buffer = bytearray()
        self.counter = 0  # счетчик байт
        self.last_node = 0
        
        # Инициализация внутреннего состояния
        self.h = list(self.IV)
        
        # Настройка параметров
        self.param = self._initialize_parameters(digest_size, key)
        
        # Если есть ключ, инициализируем им
        if key:
            block = bytearray(self.block_size)
            block[:len(key)] = key
            self._update(block, True)
        
        if data:
            self.update(data)
    
    def _initialize_parameters(self, digest_size, key):
      
        param = bytearray(64)
        
        # digest length
        param[0] = digest_size
        # key length
        param[1] = len(key)
        # fanout and depth
        param[2] = 1
        param[3] = 1
        # leaf length
        param[4:8] = (0).to_bytes(4, 'little')
        # node offset
        param[8:16] = (0).to_bytes(8, 'little')
        # node depth, inner length
        param[16] = 0
        param[17] = 0
        # reserved
        param[18:24] = bytes(6)
        # salt
        param[24:32] = bytes(8)
        # personalization
        param[32:40] = bytes(8)
        
        # XOR параметров с IV
        for i in range(8):
            self.h[i] ^= int.from_bytes(param[i*8:(i+1)*8], 'little')
        
        return param
    
    @staticmethod
    def _right_rotate(x, n):
        
        n %= 64
        return ((x >> n) | (x << (64 - n))) & ((1 << 64) - 1)
    
    def _g(self, v, a, b, c, d, x, y):
        
        v[a] = (v[a] + v[b] + x) & ((1 << 64) - 1)
        v[d] = self._right_rotate(v[d] ^ v[a], 32)
        v[c] = (v[c] + v[d]) & ((1 << 64) - 1)
        v[b] = self._right_rotate(v[b] ^ v[c], 24)
        v[a] = (v[a] + v[b] + y) & ((1 << 64) - 1)
        v[d] = self._right_rotate(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & ((1 << 64) - 1)
        v[b] = self._right_rotate(v[b] ^ v[c], 63)
        
        return v
    
    def _compress(self, block, last_block=False):
       
        # Подготовка сообщения
        m = [int.from_bytes(block[i*8:(i+1)*8], 'little') for i in range(16)]
        
        # Инициализация вектора v
        v = [0] * 16
        v[:8] = self.h
        v[8:12] = self.IV[:4]
        v[12] = self.IV[4] ^ (self.counter & 0xFFFFFFFFFFFFFFFF)
        v[13] = self.IV[5] ^ ((self.counter >> 64) & 0xFFFFFFFFFFFFFFFF)
        v[14] = self.IV[6] ^ (0xFFFFFFFFFFFFFFFF if last_block else 0)
        v[15] = self.IV[7] ^ self.last_node
        
        # 12 раундов
        for round_idx in range(12):
            s = self.SIGMA[round_idx]
            
            # Столбец раунда
            v = self._g(v, 0, 4, 8, 12, m[s[0]], m[s[1]])
            v = self._g(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
            v = self._g(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
            v = self._g(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
            
            # Диагональ раунда
            v = self._g(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
            v = self._g(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
            v = self._g(v, 2, 7, 8, 13, m[s[12]], m[s[13]])
            v = self._g(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
        
        # Обновление состояния
        for i in range(8):
            self.h[i] ^= v[i] ^ v[i + 8]
    
    def _update(self, data, is_last=False):
      
        # Разбиваем данные на блоки
        for i in range(0, len(data), self.block_size):
            block = data[i:i + self.block_size]
            
            # Если блок не полный, дополняем нулями
            if len(block) < self.block_size:
                block = block.ljust(self.block_size, b'\x00')
            
            # Увеличиваем счетчик
            self.counter += len(block)
            
            # Проверяем, последний ли это блок
            last_block = is_last and (i + self.block_size >= len(data))
            
            # Сжимаем блок
            self._compress(block, last_block)
    
    def update(self, data):
      
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Добавляем данные в буфер
        self.buffer.extend(data)
        
        # Обрабатываем полные блоки
        while len(self.buffer) >= self.block_size:
            block = self.buffer[:self.block_size]
            self._update(block)
            self.buffer = self.buffer[self.block_size:]
    
    def digest(self):
     
        # Дополнение оставшихся данных
        remaining = len(self.buffer)
        
        # Создаем финальный блок
        block = bytearray(self.block_size)
        block[:remaining] = self.buffer
        
        # Добавляем padding: 0x80 затем нули
        block[remaining] = 0x80
        
        # Если недостаточно места для счетчика (последние 16 байт)
        if remaining + 1 > self.block_size - 16:
            # Сжимаем этот блок без флага последнего блока
            self.counter += self.block_size
            self._compress(block, False)
            # Создаем новый пустой блок для счетчика
            block = bytearray(self.block_size)
        
        # Добавляем счетчик бит в конец (little-endian)
        bit_counter = self.counter * 8
        block[-16:-8] = (bit_counter & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')
        block[-8:] = ((bit_counter >> 64) & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')
        
        # Сжимаем финальный блок
        self._update(block, True)
        
        # Конвертируем состояние в байты
        result = bytearray()
        for word in self.h[:8]:  # BLAKE2b использует первые 8 слов
            result.extend(word.to_bytes(8, 'little'))
        
        return bytes(result[:self.digest_size])
    
    def hexdigest(self):
       
        return self.digest().hex()
    
    def copy(self):
       
        new_hash = BLAKE2b(digest_size=self.digest_size)
        new_hash.h = self.h.copy()
        new_hash.buffer = self.buffer.copy()
        new_hash.counter = self.counter
        new_hash.last_node = self.last_node
        new_hash.param = self.param.copy()
        return new_hash


# Функции для удобного использования
def blake2b(data=b'', digest_size=64, key=b''):

    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hasher = BLAKE2b(digest_size=digest_size, key=key)
    if data:
        hasher.update(data)
    return hasher


# Пример использования
if __name__ == "__main__":
    # Тестирование BLAKE2b-512 (по умолчанию)
    print("BLAKE2b-512 тесты:")
    
    test_cases = [
        (b"", "786a02f742015903c6c6fd852552d272912f4740e15847618a86e217f71f5419d25e1031afee585313896444934eb04b903a685b1448b755d56f701afe9be2ce"),
        (b"hello", "e4cfa39a3d37be31c59609e807970799caa68a19bfaa15135f165085e01d41a65ba1e1b146aeb6bd0092b49eac214c103ccfa3a365954bbbe52f74a2b3620c94"),
        (b"The quick brown fox jumps over the lazy dog", "a8add4bdddfd93e4877d2746e62817b116364a1fa7bc148d95090bc7333b3673f82401cf7aa2e4cb1ecd90296e3f14cb5413f8ed77be73045b13914cdcd6a918")
    ]
    
    for data, expected in test_cases:
        hasher = blake2b(data)
        result = hasher.hexdigest()
        print(f"'{data.decode() if data else 'empty'}':")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print(f"  Match:    {result == expected}")
        print()
    
    # Тестирование BLAKE2b-256
    print("\nBLAKE2b-256 тест:")
    hasher256 = blake2b(b"hello", digest_size=32)
    print(f"BLAKE2b-256('hello'): {hasher256.hexdigest()}")
