from .sha256 import SHA256
from .sha3_256 import SHA3_256
from .blake2b import BLAKE2b


def get_hash_function(name):
    """Фабрика для получения хеш-функции"""
    hash_classes = {
        'sha256': SHA256,
        'sha3-256': SHA3_256,
        'blake2b': BLAKE2b,
    }

    if name not in hash_classes:
        raise ValueError(f"Unsupported hash function: {name}")

    return hash_classes[name]()
