"""Command-line entry point for hiandbye."""

import logging
from keyword_listener import main as _main


def main() -> None:
    """Configure logging and delegate to the core keyword listener."""
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    _main()


if __name__ == "__main__":
    main()
