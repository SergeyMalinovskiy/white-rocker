import time
from collections import defaultdict
from typing import Callable

from watchdog.events import FileSystemEventHandler

from contracts.handlers import FileHandler


class YaDiskFileHandler(FileSystemEventHandler):
    def __init__(self, file_handler: FileHandler, debounce_seconds: int = 3):
        self._last_event = defaultdict(float)
        self._debounce = debounce_seconds
        self._file_handler = file_handler

    # TODO: найти более хороший способ для определения 
    def _is_duplicate(self, path: str, event_type: str) -> bool:
        """Проверяет, не дублируется ли событие."""
        key = f"{path}:{event_type}"
        now = time.time()

        if now - self._last_event[key] < self._debounce:
            return True

        self._last_event[key] = now
        return False

    def on_modified(self, event):
        if event.is_directory:
            return

        if self._is_duplicate(event.src_path, 'modified'):
            return

        print(f"[modified] {event.src_path}")

        self._file_handler(event.src_path)


