"""A Metasploit-style command line for the Red agent (skeleton).

For now it exposes only safe, non-offensive commands so you can drive and
inspect the allowlist. Attack commands are added once the executor and the
LLM planner are in place.

    pandemonium-red check http://172.16.10.10:3000     # one-shot allowlist check
    pandemonium-red console                            # interactive prompt
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_allowlist
from .exceptions import TargetNotAllowedError

DEFAULT_ALLOWLIST = Path(__file__).resolve().parent.parent / "config" / "allowlist.example.yaml"
BANNER = r"""
  Pandemonium :: Red  (CNC 418)
  lab-only · allowlist-enforced · verify-before-report
"""


def _check(allowlist, target: str) -> bool:
    try:
        host = allowlist.enforce(target)
        print(f"[+] allowed   {target}  ->  {host}")
        return True
    except TargetNotAllowedError as exc:
        print(f"[-] refused   {exc}")
        return False


def _console(allowlist_path: Path) -> None:
    allowlist = load_allowlist(allowlist_path)
    print(BANNER)
    print(f"allowlist: {allowlist_path}")
    print("commands: check <target> | show allowlist | help | exit\n")
    while True:
        try:
            line = input("red> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        if cmd in ("exit", "quit"):
            return
        elif cmd == "help":
            print("check <target> | show allowlist | help | exit")
        elif cmd == "check":
            _check(allowlist, arg.strip())
        elif cmd == "show" and arg.strip() == "allowlist":
            for net in allowlist.networks:
                print(f"  net   {net}")
            for host in sorted(allowlist.hostnames):
                print(f"  host  {host}")
        else:
            print(f"unknown command: {line!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pandemonium-red", description=__doc__)
    parser.add_argument(
        "--allowlist", type=Path, default=DEFAULT_ALLOWLIST, help="path to the allowlist file"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="check one target against the allowlist")
    p_check.add_argument("target")

    sub.add_parser("console", help="interactive prompt")

    args = parser.parse_args(argv)

    if args.command == "check":
        allowlist = load_allowlist(args.allowlist)
        return 0 if _check(allowlist, args.target) else 1
    if args.command == "console":
        _console(args.allowlist)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
