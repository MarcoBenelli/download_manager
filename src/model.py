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
    _history_file = '{}/.{}_history.json'.format(
        pathlib.Path.home(),
        os.path.splitext(os.path.basename(sys.argv[0]))[0])
    _progress_file = '{}/.{}_progress.json'.format(
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
        incomplete = []
        for job in DownloadJob._instances:
            if job._future.result():
                incomplete.append({'name': job._name, 'url': job._url})
        with open(DownloadJob._progress_file, 'w') as f:
            json.dump(incomplete, f)

    @staticmethod
    def history() -> list[dict[str, typing.Any]]:
        try:
            with open(DownloadJob._history_file) as f:
                history = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            history = []
        for job in DownloadJob._instances:
            history.append({'name': os.path.basename(job._name),
                            'url': job._url,
                            'result': job._future.result(),
                            't_start': str(job._time_started),
                            't_complete': str(job._time_completed)})
        return history

    @staticmethod
    def incomplete_from_file():
        try:
            with open(DownloadJob._progress_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return []

    def __init__(self, url: str, done: typing.Callable[[], typing.Any],
                 step: typing.Callable[[], typing.Any],
                 error: typing.Callable[[Exception], typing.Any],
                 name: str = '') -> None:
        self._url = url
        self._dir = DownloadJob.downloads_dir
        self._step_call = step
        self._done_call = done
        self._error_call = error
        self._cancel_event = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        if name:
            self._name = name
        else:
            basename = '{}/{}'.format(
                self._dir, os.path.basename(parse.urlparse(url).path))
            print(basename)
            self._name = basename
            i = 0
            while True:
                try:
                    f = open(self._name, 'xb')
                except FileExistsError:
                    i += 1
                    self._name = f'_{i}'.join(
                        os.path.splitext(basename))
                else:
                    f.close()
                    break
        print(self._name)
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
        size = os.path.getsize(self._name)
        print(f'size = {size}')
        try:
            response = request.urlopen(request.Request(
                self._url, headers={'Range': f'bytes={size}-'}))
        except Exception as exc:
            self._error_call(exc)
        else:
            try:
                remaining = int(response.getheader('Content-length'))
            except TypeError:
                print('content length not provided')
                length = 100 * 0x1000
                self._step_call = lambda: None
                flags = 'wb'
            else:
                length = size + remaining
                for _ in range(100*size//length):
                    self._step_call()
                flags = 'ab'
            with open(self._name, flags) as f:
                while buffer := response.read(length//100):
                    if DownloadJob._cancel_all_event:
                        self._time_completed = datetime.datetime.today()
                        return True
                    if self._cancel_event:
                        self._done_call()
                        self._time_completed = datetime.datetime.today()
                        return False
                    self._pause_event.wait()
                    f.write(buffer)
                    self._step_call()
        self._done_call()
        self._time_completed = datetime.datetime.today()
        return False
