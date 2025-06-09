# Modules
import stat
import mimetypes
from pathlib import Path

from htx import __version__
from htx.host import Host, Request, Response
from htx.templates import templates

# Initialization
HTML_TEMPLATE = """\
<!doctype html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">

        <!-- CSS -->
        <style>
            body, html {{
                margin: 0px;
                height: 100%;
                color: #fff;
                background: #000;
            }}
            body {{
                font-family: monospace;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }}
            div {{
                padding: 2px 10px;
                background-color: gray;
            }}
            footer {{
                display: flex;
                justify-content: space-between;
            }}
            table, hr, footer {{
                width: 600px;
                border-bottom: 0px;
            }}
            a {{
                color: #fff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline dotted;
            }}
        </style>

        <title>HTX · File Listing</title>
    </head>
    <body>
        <table>
            <thead>
                <th><div>size</div></th>
                <th><div>name</div></th>
                <th><div>perm</div></th>
            </thead>
            <tbody>
                <tr><td>0</td><td><a href = "..">..</a></td><td>dr-xr-xr-x</td></tr>
                {content}
            </tbody>
        </table>
        <hr>
        <footer>
            <span>HTX · v{version}</span>
            <span>~/{current}</span>
        </footer>
    </body>
</html>"""

# Application setup
def scaffold_app(backend: Host, args: list[str]) -> None:
    if not args:
        exit("usage: htx.serve [path]")

    path = Path(args[0])

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
                HTML_TEMPLATE.format(
                    content = "".join(_[1] for _ in sorted(directories, key = lambda _: _[0])) + "".join(_[1] for _ in sorted(files, key = lambda _: _[0])),
                    version = __version__,
                    current = str(target.relative_to(path)) if target != path else ""
                ).encode()
            )

        mime_type, _ = mimetypes.guess_type(target.name)
        return Response(200, target.read_bytes(), {"Content-Type": mime_type or "application/octet-stream"})
