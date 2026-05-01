import os
import sys
from dotenv import load_dotenv

from common.files import read_bytes
from services.lsb_encoding_service import LsbEncodingService


def main(*args, **kwargs):
    payload_image = args[0]
    carrier_image = args[1]
    output_image = args[2]
    # output_image = 'output.png'

    lsb_encoding_service = LsbEncodingService(os.getenv("LSB_PKEY"))

    payload = read_bytes(payload_image)

    lsb_encoding_service.hide_data_to_image(payload, carrier_image, output_image)

    decoded_data = lsb_encoding_service.extract_data_from_image(output_image)

    print(decoded_data == payload)



if __name__ == "__main__":
    load_dotenv()

    main(*sys.argv[1:])
