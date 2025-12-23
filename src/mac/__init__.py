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


def parse_hmac_file(filepath: str):

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            if not line:
                return "", ""

            # Разделяем по пробелам
            parts = line.split(maxsplit=1)
            if len(parts) >= 2:
                return parts[0], parts[1]
            elif len(parts) == 1:
                return parts[0], ""
            else:
                return "", ""
    except Exception as e:
        print(f"[WARNING] Error parsing HMAC file {filepath}: {e}")
        return "", ""