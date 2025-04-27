# Copyright (c) 2025 iiPython

# Modules
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from htx import __version__
from htx.host import Response
from htx.host.templates import GATEWAY_ISSUE

# Main class
class ReverseProxy:
    def __init__(self) -> None:
        pass

    async def request(self, url: str) -> Response:
        request = Request(url, headers = {"User-Agent": f"htx/{__version__} (https://github.com/iiPythonx/htx; ben@iipython.dev)"})
        try:
            with urlopen(request) as response:
                return Response(response.status, response.read(), {})

        except HTTPError as e:
            return Response(e.code, e.read(), {})

        except URLError as e:
            return Response(
                502,
                GATEWAY_ISSUE.format(code = 502, title = "BAD GATEWAY", message = e.reason).encode(),
                {}
            )

        except Exception as e:
            return Response(
                500,
                GATEWAY_ISSUE.format(code = 500, title = "INTERNAL PROXYING ISSUE", message = f"The HTX backend failed to exchange your request.<br>{e}").encode(),
                {}
            )

