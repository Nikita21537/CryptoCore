import struct
from typing import List, Union

# Константы SHA3
RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
    0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008
]

ROTATION_CONSTANTS = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14]
]


class SHA3_256:

    
    RATE = 1088  # Для SHA3-256: 1600 - 2*256 = 1088
    CAPACITY = 512
    OUTPUT_SIZE = 32  # 256 бит = 32 байта
    
    def __init__(self):
       
        self.state = [[0] * 5 for _ in range(5)]  # 5x5 матрица 64-битных слов
        self.buffer = bytearray()
        self.total_length = 0
        self._initialize_state()
    
    def _initialize_state(self):
        
        for i in range(5):
            for j in range(5):
                self.state[i][j] = 0
    
    def _keccak_f(self):
  
        for round_constant in RC:
            # Theta шаг
            C = [self.state[x][0] ^ self.state[x][1] ^ self.state[x][2] ^ 
                 self.state[x][3] ^ self.state[x][4] for x in range(5)]
            
            D = [C[(x + 4) % 5] ^ self._rotl64(C[(x + 1) % 5], 1) for x in range(5)]
            
            for x in range(5):
                for y in range(5):
                    self.state[x][y] ^= D[x]
            
            # Rho и Pi шаги
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    B[y][(2 * x + 3 * y) % 5] = self._rotl64(
                        self.state[x][y], ROTATION_CONSTANTS[x][y]
                    )
            
            # Chi шаг
            for x in range(5):
                for y in range(5):
                    self.state[x][y] = B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y])
            
            # Iota шаг
            self.state[0][0] ^= round_constant
    
    def _rotl64(self, x: int, n: int) -> int:
        
        return ((x << n) & 0xFFFFFFFFFFFFFFFF) | (x >> (64 - n))
    
    def _absorb(self):
       
        # Преобразование байтов в блоки по 64 бита
        block_count = len(self.buffer) // 8
        
        for i in range(block_count):
            # Индексы в матрице состояния
            x = i % 5
            y = (i // 5) % 5
            
            # Чтение 64-битного слова из буфера
            word = struct.unpack('<Q', self.buffer[i*8:(i+1)*8])[0]
            self.state[x][y] ^= word
        
        # Обработка неполного последнего слова
        remaining = len(self.buffer) % 8
        if remaining > 0:
            i = block_count
            x = i % 5
            y = (i // 5) % 5
            
            # Дополняем нулями до 8 байт
            padded = self.buffer[block_count*8:] + b'\x00' * (8 - remaining)
            word = struct.unpack('<Q', padded)[0]
            self.state[x][y] ^= word
        
        # Применяем перестановку Keccak
        self._keccak_f()
        self.buffer.clear()
    
    def update(self, data: Union[bytes, bytearray]):
      
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"Expected bytes, got {type(data).__name__}")
        
        self.total_length += len(data)
        self.buffer.extend(data)
        
        # Поглощаем полные блоки
        while len(self.buffer) >= self.RATE // 8:
            self._absorb()
    
    def digest(self) -> bytes:
       
        # Добавляем дополнение согласно спецификации SHA3
        # 0x06 || 0x80... (SHA3 padding)
        padding = bytearray()
        padding.append(0x06)
        
        # Вычисляем сколько байт нужно добавить
        block_size = self.RATE // 8
        bytes_in_buffer = len(self.buffer)
        
        # Добавляем 0x80 байт
        padding.extend([0x00] * (block_size - bytes_in_buffer - 2))
        padding.append(0x80)
        
        # Добавляем дополнение в буфер
        self.update(bytes(padding))
        
        # Дополнение должно поглотиться полностью
        if len(self.buffer) > 0:
            self._absorb()
        
        # Извлечение хеша (первые 32 байта состояния)
        result = bytearray()
        output_words = self.OUTPUT_SIZE // 8  # 32 байта = 4 слова
        
        for i in range(output_words):
            x = i % 5
            y = (i // 5) % 5
            word = self.state[x][y]
            result.extend(struct.pack('<Q', word))
        
        # Сбрасываем состояние для возможного повторного использования
        self._initialize_state()
        self.buffer.clear()
        self.total_length = 0
        
        return bytes(result[:self.OUTPUT_SIZE])
    
    def hexdigest(self) -> str:
       
        return self.digest().hex()


def sha3_256(data: Union[bytes, bytearray, str]) -> bytes:
   
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hasher = SHA3_256()
    hasher.update(data)
    return hasher.digest()


def sha3_256_hex(data: Union[bytes, bytearray, str]) -> str:
 
    return sha3_256(data).hex()


if __name__ == "__main__":
    # Тестовая проверка
    test_vectors = [
        (b"", "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
        (b"hello", "3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392"),
        (b"hello world", "644bcc7e564373040999aac89e7622f3ca71fba1d972fd94a31c3bfbf24e3938"),
    ]
    
    print("Testing SHA3-256 implementation:")
    for data, expected in test_vectors:
        result = sha3_256_hex(data)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{data.decode() if data else 'empty'}': {result}")
        if result != expected:
            print(f"  Expected: {expected}")
