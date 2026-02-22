#!/usr/bin/env python3
"""ContentForge — System tworzenia treści w języku polskim."""

import sys

from contentforge.cli import ContentForgeCLI


def main():
    try:
        cli = ContentForgeCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nDo zobaczenia!")
        sys.exit(0)


if __name__ == "__main__":
    main()
