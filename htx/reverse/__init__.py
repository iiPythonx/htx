# Copyright (c) 2025 iiPython

# Modules
from pathlib import Path
from http import HTTPStatus
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from htx import __version__
from htx.host import Response

# Main class
class ReverseProxy:
    def __init__(self) -> None:
        self.error_page = (Path(__file__).parents[1] / "host/templates/error.html").read_text()

    async def request(self, url: str) -> Response:
        request = Request(url, headers = {"User-Agent": f"htx/{__version__} (https://github.com/iiPythonx/htx; ben@iipython.dev)"})
        try:
            with urlopen(request) as response:
                return Response(response.status, response.read())

        except HTTPError as e:
            return Response(e.code, e.read())

        except URLError as e:
            return Response(
                HTTPStatus.BAD_GATEWAY,
                self.error_page.format(title = "BAD GATEWAY", message = e.reason).encode()
            )

        except Exception as e:
            return Response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                self.error_page.format(title = "INTERNAL PROXYING ISSUE", message = f"The HTX backend failed to exchange your request.<br>{e}").encode()
            )

