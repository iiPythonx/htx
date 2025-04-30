<div align = "center">

![HTX Logo](.github/htx.png)

A built from scratch Python HTTP server and reverse proxy.

</div>

### Synopsis

HTX is a zero-dependency HTTP server and reverse proxy built entirely from scratch as an experiment/proof of concept. It can act as a standalone HTTP server, giving low level access to the protocol, and also has reverse proxy functionality.

### Basic usage

#### HTTP

```py
import asyncio
from http import HTTPStatus

from htx.host import Host, Request, Response

backend = Host()

@backend.event("request")
async def on_request(request: Request) -> Response:
    return Response(
        HTTPStatus.OK,
        b"Hello, world!"
    )

asyncio.run(backend.start(host, port))
```

The only current event is `request`; however, depending on whether SSL termination gets added there may be more down the road.

#### Reverse Proxying

```py
import asyncio
from http import HTTPStatus

from htx.host import Request
from htx.reverse import ReverseProxy

async def main() -> None:
    proxy = ReverseProxy()
    print(await proxy.request("https://someserver.tld", Request<>))

asyncio.run(main())
```

As of right now, the reverse proxy actively requires a `htx.host.Request` object to be passed to it, which is not ideal to create by hand. In the future, this API will be accessible outside of the standard HTTP scope.

### Typing

The main types of this library are as follows:

```py
type Request {
    method:  str
    path:    str
    query:   str
    version: str              # HTTP version in use
    headers: dict[str, str]
    body:    bytes
    client:  tuple[str, int]  # Tuple of (hostname, port)
}

type Response {
    code: HTTPStatus | int
    body: bytes
    head: dict[str, str] = {}
}
```

These types can be assumed to be constant and more then likely won't be changed even as the API progresses.  
If you are using HTX and have a situation where the API is not typed very intuitively, please open a issue.

### General notice

This module is built for fun and research about HTTP in general. By no means is it code that should be deployed in production, whether for laughs or otherwise.  
If you do find any sort of security vulnerability, please feel free to open an issue for it. Confidentiality is not a requirement in this case.
