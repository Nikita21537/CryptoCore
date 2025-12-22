from typing import Union
from ..mac import HMAC


def derive_key(
        master_key: bytes,
        context: Union[str, bytes],
        length: int = 32
) -> bytes:

    if length <= 0:
        raise ValueError("Key length must be positive")

    if isinstance(context, str):
        context = context.encode('utf-8')

    derived = b''
    counter = 1

    while len(derived) < length:
        hmac = HMAC(master_key, 'sha256')
        block = hmac.compute(context + counter.to_bytes(4, 'big'))
        derived += block
        counter += 1

    return derived[:length]