from concurrent import futures
from urllib import request, parse
import pathlib
import os
import threading
import typing


class DownloadJob:
    downloads_dir = f'{pathlib.Path.home()}/Downloads'
    _executor = futures.ThreadPoolExecutor()
    _instances = []
    _cancel_all_event = False

    @staticmethod
    def create(*args, **kwargs) -> None:
        job = DownloadJob(*args, **kwargs)
        DownloadJob._instances.append(job)
        return job

    @staticmethod
    def delete_all() -> None:
        DownloadJob._cancel_all_event = True
        DownloadJob._executor.shutdown()

    def __init__(self, url: str, done: typing.Callable[[], typing.Any],
                 step: typing.Callable[[], typing.Any],
                 error: typing.Callable[[Exception], typing.Any]) -> None:
        self._url = url
        self._dir = DownloadJob.downloads_dir
        self._step_call = step
        self._done_call = done
        self._error_call = error
        self._cancel_event = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        DownloadJob._executor.submit(self._urlopen)

    def cancel(self) -> None:
        self._cancel_event = True
        self._pause_event.set()

    def toggle_pause(self) -> None:
        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    def _urlopen(self) -> None:
        print(self._url)
        try:
            response = request.urlopen(self._url)
        except Exception as exc:
            self._error_call(exc)
        else:
            print(os.path.basename(parse.urlparse(response.url).path))
            with open('{}/{}'.format(
                    self._dir,
                    os.path.basename(parse.urlparse(response.url).path)),
                    'wb') as f:
                try:
                    length = int(response.getheader('Content-length'))
                except TypeError:
                    print('content length not provided')
                    length = 100 * 0x1000
                    self._step_call = lambda: None
                while buffer := response.read(length//100):
                    if DownloadJob._cancel_all_event:
                        return
                    if self._cancel_event:
                        self._done_call()
                        return
                    self._pause_event.wait()
                    f.write(buffer)
                    self._step_call()
        self._done_call()
