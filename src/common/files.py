
def read_bytes(filepath: str) -> bytes:
    f = open(filepath, 'rb')
    data = f.read()
    f.close()
    return data
