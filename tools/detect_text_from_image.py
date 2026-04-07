import easyocr
import sys


def main(*args, **kwargs):
    reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
    result = reader.readtext(args[0]) if args else []
    print(' '.join([detection[1] for detection in result]))


if __name__ == "__main__":
    main(*sys.argv[1:])  # ← передаём аргументы командной строки
