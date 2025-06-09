# Copyright (c) 2025 iiPython

# Modules
import re
import ast
import asyncio
import argparse
import importlib
import subprocess
from shutil import which
from pathlib import Path
from importlib.util import find_spec

from htx.host import Host

# Initialization
def main() -> None:
    p = argparse.ArgumentParser(
        prog = "htx",
        description = "A built from scratch Python HTTP server with custom apps.",
        epilog = "Copyright (c) 2025 iiPython"
    )
    p.add_argument("app")
    p.add_argument("--host")
    p.add_argument("-p", "--port")

    # Handle processing
    args, unknown_args = p.parse_known_args()
    host, port = args.host or "127.0.0.1", int(args.port or 8000)

    # Load module
    spec = find_spec(args.app)
    if spec is None:
        exit(f"htx: no such module: '{args.app}'")

    # Calculate needed packages
    def load_requires() -> list[str]:
        if spec.origin is None:
            return []

        with Path(spec.origin).open() as fh:
            tree = ast.parse(fh.read(), filename = fh.name)

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__requires__":
                        return ast.literal_eval(node.value)

        return []

    needed = []
    for requirement in load_requires():
        exact_match = re.match(r"(\w+)(?:>=|===|<=|~=|>|<|==)", requirement)
        if exact_match is not None:
            exact_match = exact_match.group(1)

        package = exact_match or requirement
        if find_spec(package) is None:
            needed.append(package)

    if needed:

        # Find a suitable package manager
        available = [p for p in ["uv pip install -q", "poetry add", "pip install -q"] if which(p.split(" ")[0])]

        print(f"\033[34mApplication \033[33m'{args.app}'\033[34m requires the following packages:\033[0m")
        for need in needed:
            print(f"  \033[90m- \033[33m{need}\033[0m")

        if not available:
            exit("\n\033[90mHTX cannot automatically install them because no suitable package manager was found.\033[0m")

        value = input(f"\n\033[34mAutomatically install using \033[33m{available[0]} \033[90m(\033[32mY\033[90m/\033[31mn\033[90m)\033[34m?\033[0m ")
        if value.lower() not in ["y", "yes"]:
            exit()

        for item in needed:
            subprocess.run(available[0].split(" ") + [item])

    # Initialize app
    backend = Host()
    importlib.import_module(args.app).scaffold_app(backend, unknown_args) 

    # Launch
    asyncio.run(backend.start(host, port))