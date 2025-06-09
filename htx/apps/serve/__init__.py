# Modules
import stat
import mimetypes
from pathlib import Path

from htx import __version__
from htx.templating import Templating
from htx.host import Host, Request, Response

# Application setup
def scaffold_app(backend: Host, args: list[str]) -> None:
    if not args:
        exit("usage: htx.serve [path]")

    path = Path(args[0])
    templates = Templating(__file__)

    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        target = path / request.path[1:]
        if not target.exists():
            return Response(404, templates.fetch("error", title = "NOT FOUND", message = "Please check your URL and try again."))

        if target.is_dir():
            directories, files = [], []
            for item in target.iterdir():
                file = item.stat()
                (directories if item.is_dir() else files).append((item.name, f"<tr><td>{file.st_size if item.is_file() else 0}</td><td><a href = \"/{item.relative_to(path)}\">{item.name}</a></td><td>{stat.filemode(file.st_mode)}</td></tr>"))

            return Response(
                404,
                templates.fetch(
                    "listing",
                    content = "".join(_[1] for _ in sorted(directories, key = lambda _: _[0])) + "".join(_[1] for _ in sorted(files, key = lambda _: _[0])),
                    version = __version__,
                    current = str(target.relative_to(path)) if target != path else ""
                )
            )

        mime_type, _ = mimetypes.guess_type(target.name)
        return Response(200, target.read_bytes(), {"Content-Type": mime_type or "application/octet-stream"})
