# Copyright (c) 2025 iiPython

# Metadata
__requires__ = ["natsort>=8.4.0"]

# Modules
import stat
import argparse
import mimetypes
from pathlib import Path

from natsort import natsorted  # pyright: ignore

from htx import __version__
from htx.host import Host, Request, Response
from htx.templates import Templating

# Handle byte suffixes
def cleanup(num: int | float) -> str:
    unit = ""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if num < 1000 - 0.5:
            break

        if unit != "YB":
            num /= 1000

    return "{:.0f}{}".format(num, unit)

# Application setup
def scaffold_app(backend: Host, cmd: list[str]) -> None:

    # Parse arguments
    p = argparse.ArgumentParser(prog = "htx.apps.serve", add_help = False)
    p.add_argument("path")
    args, _ = p.parse_known_args(cmd)

    # Setup templating
    path = Path(args.path)
    templates = Templating([Path(__file__).parent / "templates"])

    # Request handling
    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        target = path / request.path[1:]
        if not target.exists():
            return Response(404, templates.fetch("error", title = "NOT FOUND", message = "Please check your URL and try again."))

        if target.is_dir():
            directories, files = [], []
            for item in target.iterdir():
                file = item.stat()
                (directories if item.is_dir() else files).append((item.name, f"<tr><td>{cleanup(file.st_size) if item.is_file() else 0}</td><td><a href = \"/{item.relative_to(path)}\">{item.name}</a></td><td>{stat.filemode(file.st_mode)}</td></tr>"))

            html = ""
            for item in [directories, files]:
                html += "".join(_[1] for _ in natsorted(item, key = lambda _: _[0]))

            return Response(
                200,
                templates.fetch(
                    "listing",
                    content = html,
                    version = __version__,
                    current = str(target.relative_to(path)) if target != path else ""
                )
            )

        mime_type, _ = mimetypes.guess_type(target.name)
        return Response(200, target.read_bytes(), {"Content-Type": mime_type or "application/octet-stream"})
