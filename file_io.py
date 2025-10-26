import sys

def read_file(filename: str) -> bytes:
    """
    Чтение файла в бинарном режиме
    """
    try:
        with open(filename, 'rb') as file:
            return file.read()
    except IOError as e:
        print(f"Ошибка чтения файла {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def write_file(filename: str, data: bytes) -> None:
    """
    Запись данных в файл в бинарном режиме
    """
    try:
        with open(filename, 'wb') as file:
            file.write(data)
    except IOError as e:
        print(f"Ошибка записи файла {filename}: {e}", file=sys.stderr)
        sys.exit(1)
