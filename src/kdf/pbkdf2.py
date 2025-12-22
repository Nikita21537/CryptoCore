import sys
import os
from typing import Union
from ..mac import HMAC


def pbkdf2_hmac_sha256(
        password: Union[str, bytes],
        salt: Union[str, bytes],
        iterations: int,
        dklen: int
) -> bytes:

    if iterations <= 0:
        raise ValueError("Iterations must be positive")

    if dklen <= 0:
        raise ValueError("Key length must be positive")

    # Convert inputs to bytes
    if isinstance(password, str):
        password = password.encode('utf-8')

    if isinstance(salt, str):
        # Check if it's hex
        try:
            # Remove any spaces or newlines
            salt_clean = salt.strip().lower()
            if all(c in '0123456789abcdef' for c in salt_clean):
                salt = bytes.fromhex(salt_clean)
            else:
                salt = salt.encode('utf-8')
        except ValueError:
            salt = salt.encode('utf-8')

    # Calculate number of blocks needed
    h_len = 32  # SHA-256 output is 32 bytes
    blocks_needed = (dklen + h_len - 1) // h_len

    derived_key = b''

    for i in range(1, blocks_needed + 1):
        # U1 = HMAC(password, salt || INT_32_BE(i))
        hmac = HMAC(password, 'sha256')
        block = hmac.compute(salt + i.to_bytes(4, 'big'))
        u_prev = block

        # XOR with remaining iterations
        for _ in range(2, iterations + 1):
            hmac = HMAC(password, 'sha256')
            u_curr = hmac.compute(u_prev)
            # XOR u_curr into block
            block = bytes(a ^ b for a, b in zip(block, u_curr))
            u_prev = u_curr

        derived_key += block

    # Return exactly dklen bytes
    return derived_key[:dklen]