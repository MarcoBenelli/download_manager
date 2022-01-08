from concurrent import futures
from urllib import request, parse
import pathlib
import os
import time
import threading
import typing


class DownloadJob:
    downloads_dir = f'{pathlib.Path.home()}/Downloads'
    _executor = futures.ThreadPoolExecutor()
    _instances = []

    @staticmethod
    def create(*args, **kwargs) -> None:
        job = DownloadJob(*args, **kwargs)
        DownloadJob._instances.append(job)
        return job

    @staticmethod
    def delete_all() -> None:
        for job in DownloadJob._instances:
            job.cancel()
        DownloadJob._executor.shutdown()

    def __init__(self, url: str, done: typing.Callable[[], typing.Any],
                 step: typing.Callable[[], typing.Any]) -> None:
        self._url = url
        self._dir = DownloadJob.downloads_dir
        self._step = step
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._future = DownloadJob._executor.submit(self._urlopen)
        self._future.add_done_callback(lambda f: print(f.exception()))
        # self._future.add_done_callback(lambda f: done())

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
            with open('{}/{}'.format(self._dir,
                                     os.path.basename(parse.urlparse(
                                         response.url).path)), 'wb') as f:
                try:
                    length = int(response.getheader('Content-length'))
                except TypeError:
                    print('content length not provided')
                    length = 100 * 0x1000
                    self._step = lambda: None
                while buffer := response.read(length//100):
                    if self._cancel_event.is_set():
                        print('download cancelled')
                        return
                    self._pause_event.wait()
                    f.write(buffer)
                    self._step()
