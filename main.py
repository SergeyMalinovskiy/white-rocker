import sys
import os

from dotenv import load_dotenv

from src.app import App


def main(*args, **kwargs):
    load_dotenv()

    config = {
        "app": {
            "cache_path": os.path.abspath('./tmp/cache'),
        },
        "yadisk": {
            'host': os.getenv('YADISK_HOST'),
            'oauth_host': os.getenv('YADISK_OAUTH_HOST'),
            "client_id": os.getenv("YADISK_CLIENT_ID"),
            "client_secret": os.getenv("YADISK_SECRET"),
            'verification_code': os.getenv("YADISK_VERIFICATION_CODE"),
        }
    }

    # print(config)

    app = App(config=config)

    app.run()


if __name__ == '__main__':
    main(*sys.argv[1:])