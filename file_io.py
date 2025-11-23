import sys

def read_file(file_path):
  
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except Exception as e:
        handle_file_error(e)

def write_file(file_path, data):
   
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
    except Exception as e:
        handle_file_error(e)

def handle_file_error(error):
   
    print(f"File error: {error}", file=sys.stderr)
    sys.exit(1)
