"""`pandemo` — the Pandemonium Red console.

Run it with no arguments to drop into the console (Metasploit-style):

    pandemo                         # banner + interactive prompt
    pandemo> check 172.16.10.10     # short commands inside

Or run a single command directly:

    pandemo check http://172.16.10.10:3000
    pandemo allow
    pandemo version

For now only safe commands exist (allowlist checks + inspection); attack
commands are added once the executor and the LLM planner are in place.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, banner
from .config import load_allowlist
from .exceptions import TargetNotAllowedError

DEFAULT_ALLOWLIST = Path(__file__).resolve().parent.parent / "config" / "allowlist.example.yaml"


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if banner.supports_color() else text


def _prompt() -> str:
    return _color("pandemo", "38;5;160") + _color(">", "38;5;243") + " "


HELP = """commands:
  check <target>     check one target against the allowlist
  allow              show the active allowlist
  clear              redraw the banner
  help               this help
  exit               leave the console"""


def _check(allowlist, target: str) -> bool:
    target = target.strip()
    if not target:
        print("usage: check <target>")
        return False
    try:
        host = allowlist.enforce(target)
        print(f"  {_color('[+] allowed', '38;5;040')}  {target}  ->  {host}")
        return True
    except TargetNotAllowedError as exc:
        print(f"  {_color('[-] refused', '38;5;196')}  {exc}")
        return False


def _show_allowlist(allowlist) -> None:
    for net in allowlist.networks:
        print(f"  net   {net}")
    for host in sorted(allowlist.hostnames):
        print(f"  host  {host}")


def _console(allowlist_path: Path) -> int:
    allowlist = load_allowlist(allowlist_path)
    print(banner.render(version=__version__, allowlist=str(allowlist_path)))
    print(f"  type {chr(39)}help{chr(39)} for commands, {chr(39)}exit{chr(39)} to quit\n")
    while True:
        try:
            line = input(_prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        if cmd in ("exit", "quit", "q"):
            return 0
        elif cmd in ("help", "?"):
            print(HELP)
        elif cmd == "check":
            _check(allowlist, arg)
        elif cmd == "allow":
            _show_allowlist(allowlist)
        elif cmd == "clear":
            print(banner.render(version=__version__, allowlist=str(allowlist_path)))
        else:
            print(f"  unknown command: {line!r}  (try 'help')")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pandemo", add_help=True, description="Pandemonium Red console")
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST, help="path to the allowlist file")
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="check one target against the allowlist")
    p_check.add_argument("target")
    sub.add_parser("allow", help="show the active allowlist")
    sub.add_parser("console", help="open the interactive console")
    sub.add_parser("version", help="print the version")

    args = parser.parse_args(argv)

    # No subcommand -> open the console (the base `pandemo`).
    if args.command in (None, "console"):
        return _console(args.allowlist)
    if args.command == "version":
        print(f"pandemo {__version__}")
        return 0

    allowlist = load_allowlist(args.allowlist)
    if args.command == "check":
        return 0 if _check(allowlist, args.target) else 1
    if args.command == "allow":
        _show_allowlist(allowlist)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
