from .ecb import AES_ECB
from .cbc import CBCMode
from .cfb import CFBMode
from .ofb import OFBMode
from .ctr import CTRMode
from .gcm import GCM
from .encrypt_then_mac import EncryptThenMAC


# Factory function for creating mode instances
def create_mode(mode_name: str, key: bytes, iv: bytes = None):

    mode_name = mode_name.upper()

    if mode_name == 'ECB':
        return AES_ECB(key)
    elif mode_name == 'CBC':
        return CBCMode(key, iv)
    elif mode_name == 'CFB':
        return CFBMode(key, iv)
    elif mode_name == 'OFB':
        return OFBMode(key, iv)
    elif mode_name == 'CTR':
        return CTRMode(key, iv)
    elif mode_name == 'GCM':
        return GCM(key, iv)
    elif mode_name in ['ETM', 'ENCRYPT_THEN_MAC']:
        # Default to CBC for Encrypt-then-MAC
        return EncryptThenMAC('CBC', key, iv)
    else:
        raise ValueError(f"Unsupported mode: {mode_name}")