
import os
import sys
from typing import Tuple, Optional

def read_file(file_path: str) -> bytes:
   
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def write_file(file_path: str, data: bytes) -> None:
   
    try:
       
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(data)
    except IOError as e:
        print(f"Error writing file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def safe_write_file(file_path: str, data: bytes, temp_suffix: str = '.tmp') -> None:
 
    temp_file = file_path + temp_suffix
    
    try:
      
        write_file(temp_file, data)
        
       
        os.replace(temp_file, file_path)
        
    except Exception as e:
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise e

def cleanup_failed_output(file_path: str):
  
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass  # Ignore cleanup errors

def handle_gcm_output(mode: str, operation: str, output_path: str, data: bytes, 
                     nonce: Optional[bytes] = None, tag: Optional[bytes] = None) -> None:

    if operation == 'encrypt' and mode == 'gcm':
      
        safe_write_file(output_path, data)
        
    elif operation == 'decrypt' and mode == 'gcm':
        
        safe_write_file(output_path, data)
    
    else:
        
        safe_write_file(output_path, data)
