from src.yadisk_publisher import YaDiskPublisher


class App:
    def __init__(self, config=None, *args, **kwargs, ):
        self._config = config


    def run(self):
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

        print(publisher)

