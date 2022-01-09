from concurrent import futures
from urllib import request, parse
import datetime
import json
import pathlib
import os
import sys
import threading
import typing


class DownloadJob:
    downloads_dir = f'{pathlib.Path.home()}/Downloads'
    _executor = futures.ThreadPoolExecutor()
    _instances = []
    _cancel_all_event = False
    _history_file = '{}/.{}_history'.format(
        pathlib.Path.home(),
        os.path.splitext(os.path.basename(sys.argv[0]))[0])

    @staticmethod
    def create(*args, **kwargs) -> None:
        job = DownloadJob(*args, **kwargs)
        DownloadJob._instances.append(job)
        return job

    @staticmethod
    def delete_all() -> None:
        DownloadJob._cancel_all_event = True
        DownloadJob._executor.shutdown()
        history = DownloadJob.history()
        with open(DownloadJob._history_file, 'w') as f:
            json.dump(history, f)

    @staticmethod
    def history() -> list[list[str, bool, str, str]]:
        try:
            with open(DownloadJob._history_file) as f:
                history = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            history = []
        for job in DownloadJob._instances:
            if job._future.done():
                history.append([os.path.basename(job._name), job._future.result(),
                                str(job._time_started), str(job._time_completed)])
        return history

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
        self._future = DownloadJob._executor.submit(self._urlopen)

    def cancel(self) -> None:
        self._cancel_event = True
        self._pause_event.set()

    def toggle_pause(self) -> None:
        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    def _urlopen(self) -> bool:
        print(self._url)
        self._time_started = datetime.datetime.today()
        try:
            response = request.urlopen(self._url)
        except Exception as exc:
            self._error_call(exc)
        else:
            basename = '{}/{}'.format(
                self._dir, os.path.basename(parse.urlparse(response.url).path))
            print(basename)
            i = 0
            self._name = basename
            while True:
                try:
                    f = open(self._name, 'xb')
                except FileExistsError:
                    i += 1
                    self._name = f'_{i}'.join(os.path.splitext(basename))
                    print(self._name)
                else:
                    break
            try:
                length = int(response.getheader('Content-length'))
            except TypeError:
                print('content length not provided')
                length = 100 * 0x1000
                self._step_call = lambda: None
            while buffer := response.read(length//100):
                if DownloadJob._cancel_all_event:
                    self._time_completed = datetime.datetime.today()
                    return False
                if self._cancel_event:
                    self._done_call()
                    self._time_completed = datetime.datetime.today()
                    return False
                self._pause_event.wait()
                f.write(buffer)
                self._step_call()
            f.close()
        self._done_call()
        self._time_completed = datetime.datetime.today()
        return True
