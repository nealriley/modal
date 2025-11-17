#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    args = sys.argv[1:]
    output_file: Path | None = None
    read_stdin = False

    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "--output-last-message" and idx + 1 < len(args):
            output_file = Path(args[idx + 1])
            idx += 1
        elif arg == "-":
            read_stdin = True
        idx += 1

    prompt = sys.stdin.read() if read_stdin else ""
    response = "ls -la"
    if "git" in prompt.lower():
        response = "git status"

    if output_file:
        output_file.write_text(response, encoding="utf-8")
    else:
        print(response)


if __name__ == "__main__":
    main()
