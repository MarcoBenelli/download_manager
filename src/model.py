from concurrent import futures
from urllib import request, parse
import os
import threading
import typing


class Model:
    _executor = futures.ThreadPoolExecutor()

    def __init__(self, url: str, done: typing.Callable[[], typing.Any],
                 step: typing.Callable[[], typing.Any]) -> None:
        self._url = url
        self._step = step
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        future = self._executor.submit(self._urlopen)
        future.add_done_callback(lambda f: print(f.exception()))
        future.add_done_callback(lambda f: done())

    def cancel(self) -> None:
        self._cancel_event.set()
        self._pause_event.set()

    def toggle_pause(self) -> None:
        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    def _urlopen(self) -> None:
        print(self._url)
        with request.urlopen(self._url) as response:
            print(os.path.basename(parse.urlparse(response.url).path))
            with open(os.path.basename(parse.urlparse(response.url).path),
                      'wb') as f:
                while buffer := response.read(
                        int(response.getheader('Content-length'))//100):
                    if self._cancel_event.is_set():
                        return
                    self._pause_event.wait()
                    f.write(buffer)
                    self._step()
