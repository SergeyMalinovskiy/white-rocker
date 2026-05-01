import sys
from stegano import lsb


def main(*args, **kwargs):
    #print(' '.join([detection[1] for detection in result]))
    file_path = args[0]
    print('Hiding message from file "{}"'.format(file_path))

    secret = lsb.hide(file_path, 'Amazing test hiding message')
    secret.save("output.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
