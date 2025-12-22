from .sha256 import SHA256
from .sha3_256 import SHA3_256


def create_hash(algorithm: str):

    algorithm = algorithm.lower().replace('-', '').replace('_', '')

    if algorithm == 'sha256':
        return SHA256()
    elif algorithm in ['sha3256', 'sha3_256', 'sha3']:
        return SHA3_256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def hash_data(data: bytes, algorithm: str = 'sha256') -> bytes:

    hash_obj = create_hash(algorithm)
    hash_obj.update(data)
    return hash_obj.digest()


def hash_data_hex(data: bytes, algorithm: str = 'sha256') -> str:

    return hash_data(data, algorithm).hex()


def hash_file(filepath: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:

    hash_obj = create_hash(algorithm)

    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()