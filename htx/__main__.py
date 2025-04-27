# Copyright (c) 2025 iiPython

# Modules
import asyncio
from htx.routing import scaffold_app

# Initialization
def main() -> None:
    asyncio.run(scaffold_app("localhost", 8000))
