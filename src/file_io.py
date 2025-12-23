import sys
import os
from typing import Tuple, Optional


def read_file_with_iv(filepath: str, has_iv: bool = False) -> Tuple[Optional[bytes], bytes]:

    try:
        with open(filepath, 'rb') as f:
            if has_iv:
                iv = f.read(16)
                if len(iv) != 16:
                    raise ValueError("File too short to contain IV")
                data = f.read()
                return iv, data
            else:
                data = f.read()
                return None, data
    except IOError as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def read_gcm_file(filepath: str) -> Tuple[bytes, bytes, bytes]:

    try:
        with open(filepath, 'rb') as f:
            nonce = f.read(12)
            if len(nonce) != 12:
                raise ValueError("File too short for GCM nonce")

            # Read the rest
            remaining = f.read()
            if len(remaining) < 16:
                raise ValueError("File too short for GCM tag")

            tag = remaining[-16:]
            ciphertext = remaining[:-16]

        return nonce, ciphertext, tag
    except IOError as e:
        print(f"Error reading GCM file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def read_etm_file(filepath: str, has_iv: bool = True) -> Tuple[Optional[bytes], bytes, bytes]:

    try:
        with open(filepath, 'rb') as f:
            if has_iv:
                iv = f.read(16)
                if len(iv) != 16:
                    raise ValueError("File too short for IV")
                remaining = f.read()
            else:
                iv = None
                remaining = f.read()

            if len(remaining) < 32:
                raise ValueError("File too short for HMAC tag")

            tag = remaining[-32:]
            ciphertext = remaining[:-32]

        return iv, ciphertext, tag
    except IOError as e:
        print(f"Error reading ETM file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def write_file_with_iv(filepath: str, iv: Optional[bytes], data: bytes) -> None:

    try:
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        with open(filepath, 'wb') as f:
            if iv:
                f.write(iv)
            f.write(data)
    except IOError as e:
        print(f"Error writing file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def write_gcm_file(filepath: str, nonce: bytes, ciphertext: bytes, tag: bytes) -> None:

    write_file_with_iv(filepath, nonce, ciphertext + tag)


def write_etm_file(filepath: str, iv: Optional[bytes], ciphertext: bytes, tag: bytes) -> None:

    write_file_with_iv(filepath, iv, ciphertext + tag)