# Copyright (c) 2025 iiPython

# Modules
import sys
import asyncio
import importlib

from htx.host import Host

# Initialization
def main() -> None:
    backend = Host()
    importlib.import_module(sys.argv[1]).scaffold_app(backend, sys.argv[2:])
    asyncio.run(backend.start("127.0.0.1", 8000))