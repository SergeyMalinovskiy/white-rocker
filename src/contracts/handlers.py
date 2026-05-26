from typing import Callable

from watchdog.events import FileSystemEventHandler

FilePath = str
FileHandler = Callable[[FileSystemEventHandler, FilePath], None]