from .hmac import HMAC, HMACStream
from .cmac import AESCMAC


def create_mac(algorithm: str, key: bytes):

    algorithm = algorithm.lower().replace('-', '').replace('_', '')

    if algorithm in ['hmacsha256', 'hmac']:
        return HMAC(key, 'sha256')
    elif algorithm in ['cmacaes', 'cmac']:
        return AESCMAC(key)
    else:
        raise ValueError(f"Unsupported MAC algorithm: {algorithm}")


def compute_mac(data: bytes, algorithm: str, key: bytes) -> bytes:

    mac = create_mac(algorithm, key)
    return mac.compute(data)


def compute_mac_hex(data: bytes, algorithm: str, key: bytes) -> str:

    return compute_mac(data, algorithm, key).hex()


def verify_mac(data: bytes, algorithm: str, key: bytes, mac: bytes) -> bool:

    mac_obj = create_mac(algorithm, key)
    return mac_obj.verify(data, mac)