#!/usr/bin/env python3
"""Codex tmux-based service manager for backend lifecycle/state reporting."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / ".run"
LOG_DIR = ROOT / ".logs"
PID_FILE = RUN_DIR / "backend.pid"
LOG_FILE = LOG_DIR / "backend.log"
TMUX_DIR = RUN_DIR / "tmux"
TMUX_SESSION = os.getenv("SERVICE_TMUX_SESSION", "backend_service")
TMUX_SOCKET = TMUX_DIR / f"{TMUX_SESSION}.sock"
REQUIREMENTS = ROOT / "backend" / "requirements.txt"
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", "8000"))
CODESPACE_NAME = os.getenv("CODESPACE_NAME")


def ensure_dirs() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TMUX_DIR.mkdir(parents=True, exist_ok=True)


def check_tmux_available() -> None:
    if shutil.which("tmux") is None:
        raise SystemExit("tmux not found. Install tmux or run inside Codespaces where it is available.")


def install_deps(verbose: bool = True) -> None:
    if not REQUIREMENTS.exists():
        return
    if verbose:
        print("Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)


def tmux_env() -> dict[str, str]:
    env = os.environ.copy()
    env["TMUX_TMPDIR"] = str(TMUX_DIR)
    return env


def tmux_cmd(*args: str) -> list[str]:
    return ["tmux", "-S", str(TMUX_SOCKET), *args]


def tmux_session_exists() -> bool:
    result = subprocess.run(
        tmux_cmd("has-session", "-t", TMUX_SESSION),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=tmux_env(),
    )
    return result.returncode == 0


def tmux_pane_pid() -> Optional[int]:
    if not tmux_session_exists():
        return None
    try:
        output = subprocess.check_output(
            tmux_cmd("list-panes", "-t", TMUX_SESSION, "-F", "#{pane_pid}"),
            stderr=subprocess.DEVNULL,
            env=tmux_env(),
        )
    except subprocess.CalledProcessError:
        return None
    text = output.decode().strip().splitlines()
    if not text:
        return None
    try:
        return int(text[0])
    except ValueError:
        return None


def is_running() -> tuple[bool, Optional[int]]:
    pid = None
    if tmux_session_exists():
        pid = tmux_pane_pid()
    if pid:
        PID_FILE.write_text(str(pid), encoding="utf-8")
        return True, pid
    PID_FILE.unlink(missing_ok=True)
    return False, None


def start_service(host: str, port: int, skip_install: bool) -> None:
    if tmux_session_exists():
        pid = tmux_pane_pid()
        print(f"Backend already running in tmux session '{TMUX_SESSION}' (PID {pid or 'unknown'})")
        return
    check_tmux_available()
    ensure_dirs()
    if not skip_install:
        install_deps(verbose=True)
    LOG_FILE.touch(exist_ok=True)
    env = tmux_env()
    env.update({"HOST": host, "PORT": str(port)})
    command = (
        f"cd {ROOT} && "
        f"exec bash -lc \"uvicorn backend.app.main:app --host {host} --port {port} 2>&1 | tee -a {LOG_FILE}\""
    )
    subprocess.run(tmux_cmd("new-session", "-d", "-s", TMUX_SESSION, command), check=True, env=env)
    pid = tmux_pane_pid()
    if pid:
        PID_FILE.write_text(str(pid), encoding="utf-8")
    print(f"Started backend in tmux session '{TMUX_SESSION}' (PID {pid or 'unknown'}) on {host}:{port}")
    time.sleep(1)


def stop_service() -> None:
    if not tmux_session_exists():
        print("Backend is not running.")
        PID_FILE.unlink(missing_ok=True)
        return
    subprocess.run(tmux_cmd("send-keys", "-t", TMUX_SESSION, "C-c"), check=False, env=tmux_env())
    time.sleep(0.5)
    subprocess.run(tmux_cmd("kill-session", "-t", TMUX_SESSION), check=False, env=tmux_env())
    pid = PID_FILE.read_text().strip() if PID_FILE.exists() else None
    PID_FILE.unlink(missing_ok=True)
    print(f"Stopped backend (PID {pid or 'unknown'}).")


def tail_log(lines: int = 20) -> Iterable[str]:
    if not LOG_FILE.exists():
        return []
    dq: deque[str] = deque(maxlen=lines)
    with LOG_FILE.open(encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            dq.append(line.rstrip())
    return list(dq)


def tmux_logs(lines: int) -> list[str]:
    if not tmux_session_exists():
        return []
    try:
        output = subprocess.check_output(
            tmux_cmd("capture-pane", "-t", TMUX_SESSION, "-p", "-S", f"-{lines}"),
            env=tmux_env(),
        )
        return output.decode().splitlines()
    except subprocess.CalledProcessError:
        return []


def derive_public_url(port: int) -> Optional[str]:
    codespace = os.getenv("CODESPACE_NAME")
    if codespace:
        return f"https://{codespace}-{port}.app.github.dev"
    return None


def gh_port_visibility(port: int) -> Optional[str]:
    if not CODESPACE_NAME or shutil.which("gh") is None:
        return None
    try:
        result = subprocess.run(
            [
                "gh",
                "codespace",
                "ports",
                "--codespace",
                CODESPACE_NAME,
                "--json",
                "sourcePort,visibility",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    try:
        import json

        data = json.loads(result.stdout)
    except Exception:
        return None
    for entry in data:
        if entry.get("sourcePort") == port:
            return entry.get("visibility")
    return None


def gh_set_port_visibility(port: int, visibility: str) -> bool:
    if not CODESPACE_NAME or shutil.which("gh") is None:
        return False
    try:
        subprocess.run(
            [
                "gh",
                "codespace",
                "ports",
                "visibility",
                "-c",
                CODESPACE_NAME,
                f"{port}:{visibility}",
            ],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(
            "Failed to change port visibility via gh CLI. Ensure `gh auth login` has been run.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return False


def print_status(host: str, port: int) -> None:
    running, pid = is_running()
    public_url = derive_public_url(port)
    visibility = gh_port_visibility(port)
    print("Service status:", "RUNNING" if running else "STOPPED")
    print(f"  PID: {pid or '-'}")
    print(f"  tmux session: {TMUX_SESSION if tmux_session_exists() else 'none'}")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    if visibility:
        print(f"  Port visibility: {visibility.upper()}")
    else:
        print("  Port visibility: unknown (run `gh auth login`?)")
    if public_url:
        print(f"  Public URL (make port public): {public_url}")
    else:
        print("  Public URL: unavailable")
    print("  Log tail:")
    for line in tail_log():
        print(f"    {line}")
    if not running:
        print("Use `python scripts/service_manager.py start` to launch the backend.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage backend service lifecycle via tmux")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start backend service")
    start.add_argument("--host", default=DEFAULT_HOST)
    start.add_argument("--port", type=int, default=DEFAULT_PORT)
    start.add_argument("--skip-install", action="store_true", help="Skip pip install step")

    sub.add_parser("stop", help="Stop backend service")

    restart = sub.add_parser("restart", help="Restart backend service")
    restart.add_argument("--host", default=DEFAULT_HOST)
    restart.add_argument("--port", type=int, default=DEFAULT_PORT)
    restart.add_argument("--skip-install", action="store_true")

    status = sub.add_parser("status", help="Print backend status")
    status.add_argument("--host", default=DEFAULT_HOST)
    status.add_argument("--port", type=int, default=DEFAULT_PORT)

    logs = sub.add_parser("logs", help="Show backend logs")
    logs.add_argument("-n", "--lines", type=int, default=80)
    logs.add_argument("--tmux", action="store_true", help="Read live logs from tmux pane")

    ensure_cmd = sub.add_parser("ensure", help="Start backend if not already running")
    ensure_cmd.add_argument("--host", default=DEFAULT_HOST)
    ensure_cmd.add_argument("--port", type=int, default=DEFAULT_PORT)
    ensure_cmd.add_argument("--skip-install", action="store_true")

    sub.add_parser("attach", help="Attach to tmux session")

    visibility = sub.add_parser("visibility", help="View or set port visibility")
    visibility.add_argument("--port", type=int, default=DEFAULT_PORT)
    visibility.add_argument("--mode", choices=["public", "private"], required=False)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "start":
        start_service(args.host, args.port, args.skip_install)
    elif args.command == "stop":
        stop_service()
    elif args.command == "restart":
        stop_service()
        start_service(args.host, args.port, args.skip_install)
    elif args.command == "status":
        print_status(args.host, args.port)
    elif args.command == "logs":
        lines = tmux_logs(args.lines) if args.tmux else tail_log(args.lines)
        if not lines:
            print("No logs available. Run status or ensure the service is running.")
        else:
            for line in lines:
                print(line)
    elif args.command == "ensure":
        running, _ = is_running()
        if running:
            print("Backend already running.")
        else:
            start_service(args.host, args.port, args.skip_install)
    elif args.command == "attach":
        if not tmux_session_exists():
            print("tmux session not running. Start the service first.")
        else:
            tmux_binary = shutil.which("tmux") or "tmux"
            os.execve(tmux_binary, ["tmux", "-S", str(TMUX_SOCKET), "attach", "-t", TMUX_SESSION], tmux_env())
    elif args.command == "visibility":
        current = gh_port_visibility(args.port)
        if args.mode:
            success = gh_set_port_visibility(args.port, args.mode)
            if success:
                print(f"Set port {args.port} visibility to {args.mode.upper()}.")
                current = gh_port_visibility(args.port)
        if current:
            print(f"Port {args.port} visibility: {current.upper()}")
        else:
            print("Unable to determine port visibility. Ensure gh CLI is authenticated (`gh auth login`).")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
