import sys
import os
from datetime import datetime

from cylmore_steganography_kit.src.cylmore_steganography_kit.lsb_encoding_service import LsbEncodingService
from cylmore_steganography_kit.src.cylmore_steganography_kit.masking.lsb_stegosphere_masking import \
    LsbStegosphereMasking


def main(*args, **kwargs):
    lsb_encoding_service = LsbEncodingService(
        "ff6c23048b1c40a68f658deb15485e8c",
        LsbStegosphereMasking()
    )

    print(lsb_encoding_service)

    config = {
        "app": {
            "tmpdir": os.path.abspath("../tmp"),
        },
    }

    file_path = config["app"]["tmpdir"] + '\\images\\maycat.png'

    file_data = b''
    with open(file_path, "rb") as f:
        file_data = f.read()

    print(file_data)

    image_path = os.path.join('test1.png')

    lsb_encoding_service.hide_data(file_data, image_path, datetime.now().strftime('IMG_%Y%m%d_%H%M%S.png'))

    # extracted_data = lsb_encoding_service.extract_data('test1.png')

    # print(extracted_data)


if __name__ == '__main__':
    main(*sys.argv[1:])