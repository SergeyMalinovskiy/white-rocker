import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from src.app import App



# Добавляем libs в пути поиска модулей
sys.path.insert(0, str(Path(__file__).parent.parent / 'libs'))

def main(*args, **kwargs):
    load_dotenv()

    config = {
        "app": {
            "tmpdir": os.path.abspath("./tmp"),
            "cache_path": os.path.abspath('./tmp/cache'),
            "log_file": os.path.abspath(f"./logs/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"),
            "sync_methods": os.getenv('ACTIVE_SYNC_METHODS').split(','),
        },
        'data': {
            "images_path": os.path.abspath("./data/images"),
        },
        "yadisk": {
            'host': os.getenv('YADISK_HOST'),
            'oauth_host': os.getenv('YADISK_OAUTH_HOST'),
            "client_id": os.getenv("YADISK_CLIENT_ID"),
            "client_secret": os.getenv("YADISK_SECRET"),
            'verification_code': os.getenv("YADISK_VERIFICATION_CODE"),
            'sync_dir': os.getenv("YADISK_SYNC_DIR"),
        },
        'mailru': {
            'imap_host':      os.getenv('MAILRU_IMAP_HOST'),
            'imap_port':      os.getenv('MAILRU_IMAP_PORT'),
            'smtp_host': os.getenv('MAILRU_SMTP_HOST'),
            'smtp_port': os.getenv('MAILRU_SMTP_PORT'),
            'recipient': os.getenv('MAILRU_RECIPIENT_ID'),
            'sender':    os.getenv('MAILRU_SENDER_ID'),
            'username':  os.getenv('MAILRU_USERNAME'),
            'app_pass':  os.getenv('MAILRU_APP_PASS'),
        },
        'finalazer': {
            'host': os.getenv('FINALAZER_HOST'),
            'port': os.getenv('FINALAZER_PORT'),
            'token': os.getenv('FINALAZER_TOKEN'),
        }
    }

    app = App(config=config)

    app.run()


if __name__ == '__main__':
    main(*sys.argv[1:])