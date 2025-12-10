

class SHA3_256:
  
    
    def __init__(self, data=b''):
        # Параметры для SHA3-256
        self.rate = 1088  # бит (136 байт)
        self.capacity = 512  # бит
        self.output_length = 256  # бит (32 байта)
        self.block_size = self.rate // 8  # 136 байт
        
        # Инициализация состояния Keccak (5x5 матрица 64-битных слов)
        # Всего 1600 бит = 25 слов × 64 бита
        self.state = [0] * 25
        
        # Буфер для необработанных данных
        self.buffer = bytearray()
        
        # Инициализация параметров Keccak
        self.digest_size = self.output_length // 8  # 32 байта
        
        # Константы для алгоритма Keccak
        self.rotation_constants = [
            [0, 1, 62, 28, 27],
            [36, 44, 6, 55, 20],
            [3, 10, 43, 25, 39],
            [41, 45, 15, 21, 8],
            [18, 2, 61, 56, 14]
        ]
        
        # Константы раундов
        self.round_constants = [
            0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
            0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
            0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
            0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
            0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
            0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
            0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
            0x8000000000008080, 0x0000000080000001, 0x8000000080008008
        ]
        
        if data:
            self.update(data)
    
    def _rotate_left(self, x, n):
      
        n %= 64
        return ((x << n) | (x >> (64 - n))) & ((1 << 64) - 1)
    
    def _keccak_f(self, state):
        
        # 24 раунда
        for round_idx in range(24):
            # Этап θ (theta)
            c = [0] * 5
            d = [0] * 5
            
            # Вычисляем parity столбцов
            for x in range(5):
                c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20]
            
            for x in range(5):
                d[x] = c[(x - 1) % 5] ^ self._rotate_left(c[(x + 1) % 5], 1)
            
            for x in range(5):
                for y in range(5):
                    state[x + 5 * y] ^= d[x]
            
            # Этап ρ (rho) и π (pi)
            temp_state = state.copy()
            for x in range(5):
                for y in range(5):
                    new_x = y
                    new_y = (2 * x + 3 * y) % 5
                    state[new_x + 5 * new_y] = self._rotate_left(
                        temp_state[x + 5 * y],
                        self.rotation_constants[x][y]
                    )
            
            # Этап χ (chi)
            temp_state = state.copy()
            for x in range(5):
                for y in range(5):
                    state[x + 5 * y] = temp_state[x + 5 * y] ^ (
                        (~temp_state[(x + 1) % 5 + 5 * y]) & 
                        temp_state[(x + 2) % 5 + 5 * y]
                    )
            
            # Этап ι (iota) - добавление константы раунда
            state[0] ^= self.round_constants[round_idx]
        
        return state
    
    def _absorb(self):
       
        # Разбиваем буфер на блоки по 136 байт
        for i in range(0, len(self.buffer), self.block_size):
            block = self.buffer[i:i + self.block_size]
            
            # Дополняем блок если нужно
            if len(block) < self.block_size:
                block = block.ljust(self.block_size, b'\x00')
            
            # Преобразуем блок в 64-битные слова
            block_words = []
            for j in range(0, self.block_size, 8):
                word = 0
                for k in range(8):
                    if j + k < len(block):
                        word |= (block[j + k] << (8 * k))
                block_words.append(word)
            
            # XOR с состоянием
            for j in range(len(block_words)):
                self.state[j] ^= block_words[j]
            
            # Применяем функцию перестановки
            self.state = self._keccak_f(self.state)
        
        # Очищаем буфер
        self.buffer = bytearray()
    
    def update(self, data):
       
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Добавляем данные в буфер
        self.buffer.extend(data)
        
        # Если буфер достаточно большой, поглощаем данные
        while len(self.buffer) >= self.block_size:
            self._absorb()
    
    def digest(self):
     
        # Делаем копию состояния для работы
        state_copy = self.state.copy()
        buffer_copy = self.buffer.copy()
        
        # Добавляем дополнение: 0x06 + нули + 0x80
        # Для SHA3: дополнение = 0x06 || 0x80...
        self.buffer.append(0x06)  # SHA3 использует 0x06
        # Дополняем до block_size - 1
        while len(self.buffer) % self.block_size != self.block_size - 1:
            self.buffer.append(0x00)
        self.buffer.append(0x80)
        
        # Поглощаем дополненный блок
        self._absorb()
        
        # Фаза выжимания (squeezing)
        # Для SHA3-256 нам нужно 32 байта = 4 слова по 64 бита
        result = bytearray()
        
        # Преобразуем состояние в байты
        while len(result) < self.digest_size:
            # Берем первые rate бит из состояния
            for i in range(self.block_size // 8):
                word = self.state[i]
                for j in range(8):
                    if len(result) < self.digest_size:
                        result.append((word >> (8 * j)) & 0xFF)
            
            # Если нужно больше данных, применяем перестановку
            if len(result) < self.digest_size:
                self.state = self._keccak_f(self.state)
        
        # Восстанавливаем оригинальное состояние
        self.state = state_copy
        self.buffer = buffer_copy
        
        return bytes(result[:self.digest_size])
    
    def hexdigest(self):
       
        return self.digest().hex()
    
    def copy(self):
        """Создает копию объекта хэша"""
        new_hash = SHA3_256()
        new_hash.state = self.state.copy()
        new_hash.buffer = self.buffer.copy()
        return new_hash


# Функция для удобного использования
def sha3_256(data=b''):
  
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hasher = SHA3_256(data)
    return hasher


# Пример использования
if __name__ == "__main__":
    # Тестирование
    test_cases = [
        b"",
        b"hello",
        b"hello world",
        b"The quick brown fox jumps over the lazy dog",
        b"The quick brown fox jumps over the lazy dog."
    ]
    
    for test in test_cases:
        hasher = sha3_256(test)
        print(f"'{test.decode() if test else 'empty'}':")
        print(f"  {hasher.hexdigest()}")
        print()
