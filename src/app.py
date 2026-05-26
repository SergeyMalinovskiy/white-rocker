import logging
import time
from pathlib import Path

# from stegano import lsb
from watchdog.observers import Observer
from datetime import datetime

from contracts.handlers import FilePath
from cylmore_steganography_kit.src.cylmore_steganography_kit.lsb_encoding_service import LsbEncodingService
from cylmore_steganography_kit.src.cylmore_steganography_kit.masking.lsb_stegosphere_masking import \
    LsbStegosphereMasking
from distributors.sync.mail_distributor import MailDistributor
from handlers.sync.idle_handler import SyncIdleHandler
from handlers.sync.pydroid_scaner_handler import PydroidScannerHandler
from handlers.yadisk_files_handler import YaDiskFileHandler
from publishers.mail_publisher import MailPublisher
from publishers.mailru_publisher import MailRuPublisher
from src.publishers.yadisk_publisher import YaDiskPublisher


def _save_file(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)

    print(f"Saved file \"{path}\" ...")


class App:
    def __init__(self, config=None, *args, **kwargs, ):
        self._config = config

        self._lsb_encoding_service = LsbEncodingService(
            "ff6c23048b1c40a68f658deb15485e8c",
            LsbStegosphereMasking()
        )

        self._init_logging()

    def _default_file_handler(self, _, path: FilePath) -> None:

        msg = " "
        try:
            extracted = self._lsb_encoding_service.extract_data(path)

            msg += f"{path} -> {extracted}"

            filename = datetime.now().strftime('IMG_%Y%m%d_%H%M%S')
            _save_file(f"{self._config['data']['images_path']}\\{filename}.png", extracted)
        except Exception as e:
            msg += str(e)
        finally:
            logging.info(msg)
            # print(msg)

    def run(self):
        mail_publisher = MailPublisher(
            self._config.get('mailru').get('imap_host'),
            self._config.get('mailru').get('imap_port'),
            self._config.get('mailru').get('username'),
            self._config.get('mailru').get('app_pass'),
            self._config.get('mailru').get('sender'),
            self._config.get('mailru').get('recipient'),
            self._config.get('data').get('images_path'),
        )

        mail_publisher.add_listener(
            PydroidScannerHandler(
                MailDistributor(
                    self._config.get('mailru').get('smtp_host'),
                    self._config.get('mailru').get('smtp_port'),
                    self._config.get('mailru').get('username'),
                    self._config.get('mailru').get('app_pass'),
                )
            )
        )
        mail_publisher.add_listener(SyncIdleHandler())

        mail_publisher.authorize()

        print(mail_publisher.get_listeners())

        mail_publisher.listen()
        # sync_dir_unix = Path(self._config['yadisk']['sync_dir'])
        #
        # event_handler = YaDiskFileHandler(
        #     file_handler=self._default_file_handler
        # )
        # observer = Observer()
        # observer.schedule(event_handler, str(sync_dir_unix), recursive=False)
        #
        # observer.start()
        # print(f"Start watching for folder \"{sync_dir_unix}\" ...")
        #
        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     observer.stop()
        # observer.join()

        # event_handler = MyHandler()
        # observer = Observer()
        # observer.schedule(event_handler, path_to_watch, recursive=False)  # recursive=True для вложенных папок
        # observer.start()
        #
        # print(f"Начинаем следить за папкой: {path_to_watch}")
        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     observer.stop()
        # observer.join()


        #
        # image_proxy = ImageProxy(read_bytes(image_path), 'maycat.jpg')
        # print(image_proxy.get_hash())
        #
        # def handler(proxy: IHasData) -> None:
        #     print(proxy.get_hash())
        #
        # publisher.add_poller(image_proxy, 1, handler)
        # publisher.add_poller(image_proxy, 2, handler)
        # publisher.add_poller(image_proxy, 2, handler)
        # # publisher.publish(image_path, 'maycat.png')
        #
        # #
        #
        # print(publisher.get_pollers())

        # publisher.watch_on(2, handler)



    def test(self):
        publisher = YaDiskPublisher(
            # TODO: заменить эти параметры на какой нибудь YadiskConfig датакласс
            self._config['yadisk']['host'],
            self._config['yadisk']['oauth_host'],
            self._config['yadisk']['client_id'],
            self._config['yadisk']['client_secret'],
            self._config['yadisk']['verification_code'],
            self._config['app']['cache_path'],
        )

        publisher.authorize()

        publisher.get_metadata('maycat.jpg')


    def _init_logging(self):
        normalized_path = (self._config['app']['log_file']).replace("\\", "/")

        logging.basicConfig(
            filename=normalized_path,  # имя файла лога
            level=logging.INFO,  # уровень записи
            format='[%(asctime)s] %(message)s'
        )
