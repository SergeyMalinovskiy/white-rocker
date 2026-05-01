import os.path
import time
from pathlib import Path

from stegano import lsb
from watchdog.observers import Observer

from contracts.handlers import FilePath
from handlers.yadisk_files_handler import YaDiskFileHandler
from src.publishers.yadisk_publisher import YaDiskPublisher


def default_file_handler(path: FilePath) -> None:
    print('Bytes', lsb.reveal(path))

class App:
    def __init__(self, config=None, *args, **kwargs, ):
        self._config = config

    def run(self):
        sync_dir_unix = Path(self._config['yadisk']['sync_dir'])

        event_handler = YaDiskFileHandler(
            file_handler=default_file_handler
        )
        observer = Observer()
        observer.schedule(event_handler, str(sync_dir_unix), recursive=False)

        observer.start()
        print(f"Start watching for folder \"{sync_dir_unix}\" ...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

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
