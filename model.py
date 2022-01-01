from concurrent import futures
from urllib import request, parse
import http
import os
import typing


class Model:
    _executor = futures.ThreadPoolExecutor()

    @classmethod
    def submit_url(cls, url: str, done: typing.Callable[[], typing.Any],
                   step: typing.Callable[[], typing.Any]) -> None:
        future = cls._executor.submit(cls._urlopen, url, step)
        future.add_done_callback(lambda f: print(f.exception()))
        future.add_done_callback(lambda f: done())

    @staticmethod
    def _urlopen(url: str, step: typing.Callable[[], typing.Any]) -> None:
        print(url)
        with request.urlopen(url) as response:
            print(os.path.basename(parse.urlparse(response.url).path))
            with open(os.path.basename(parse.urlparse(response.url).path),
                      'xb') as f:
                while buffer := response.read(
                        int(response.getheader('content-length'))//100):
                    f.write(buffer)
                    step()
