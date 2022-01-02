from concurrent import futures
from urllib import request, parse
import http
import os
import threading
import typing


class Model:
    _executor = futures.ThreadPoolExecutor()

    @classmethod
    def submit_url(cls, url: str, done: typing.Callable[[], typing.Any], step: typing.Callable[[], typing.Any]) -> tuple[threading.Event, threading.Event]:
        cancel = threading.Event()
        pause = threading.Event()
        pause.set()
        future = cls._executor.submit(cls._urlopen, url, step, cancel, pause)
        future.add_done_callback(lambda f: print(f.exception()))
        future.add_done_callback(lambda f: done())
        return cancel, pause

    @staticmethod
    def _urlopen(url: str, step: typing.Callable[[], typing.Any], cancel: threading.Event, pause: threading.Event) -> None:
        print(url)
        with request.urlopen(url) as response:
            print(os.path.basename(parse.urlparse(response.url).path))
            with open(os.path.basename(parse.urlparse(response.url).path),
                      'wb') as f:
                while buffer := response.read(
                        int(response.getheader('Content-length'))//100):
                    if cancel.is_set():
                        return
                    pause.wait()
                    f.write(buffer)
                    step()
