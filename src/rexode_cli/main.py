import sys
import os

# Add the current directory to sys.path if not already present
# This is to ensure modules within 'src' are discoverable when run from project root
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import asyncio
from .cli import CLI

def main():
    cli = CLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
