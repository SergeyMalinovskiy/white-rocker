import sys
import os

from cylmore_steganography_kit.src.cylmore_steganography_kit.lsb_encoding_service import LsbEncodingService
from cylmore_steganography_kit.src.cylmore_steganography_kit.masking.lsb_stegosphere_masking import \
    LsbStegosphereMasking


def main(*args, **kwargs):
    lsb_encoding_service = LsbEncodingService(
        "ff6c23048b1c40a68f658deb15485e8d",
        LsbStegosphereMasking()
    )

    print(lsb_encoding_service)

    config = {
        "app": {
            "tmpdir": os.path.abspath("../tmp"),
        },
    }

    image_path = os.path.join(config['app']['tmpdir'], 'images', 'maycat.png')

    test_data = b'test data'

    lsb_encoding_service.hide_data(test_data, image_path, 'output1.png')

    extracted_data = lsb_encoding_service.extract_data('output1.png')

    print(extracted_data)


if __name__ == '__main__':
    main(*sys.argv[1:])