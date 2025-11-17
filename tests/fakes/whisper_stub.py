#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    args = sys.argv[1:]
    audio_path: Path | None = None
    output_prefix: Path | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-f" and i + 1 < len(args):
            audio_path = Path(args[i + 1])
            i += 1
        elif arg == "-of" and i + 1 < len(args):
            output_prefix = Path(args[i + 1])
            i += 1
        i += 1

    if audio_path is None or not audio_path.exists():
        print("missing or invalid -f argument", file=sys.stderr)
        sys.exit(1)
    if output_prefix is None:
        print("missing -of argument", file=sys.stderr)
        sys.exit(1)

    txt_path = output_prefix.with_suffix(".txt")
    txt_path.write_text("stub transcript", encoding="utf-8")


if __name__ == "__main__":
    main()
