"""The Pandemonium console banner (ASCII art, shown on launch)."""
from __future__ import annotations

import os
import re
import sys

_RESET = "\033[0m"
_BOLD = "\033[1m"
_FOG = "38;5;250"     # pale mist
_SMOKE = "38;5;243"   # grey (box border)
_EYE = "38;5;196"     # glowing red
_INK = "38;5;196"     # bright red (box text, main line)
_INK2 = "38;5;160"    # blood red (box text, secondary lines)
# Flame gradient for the wordmark, bright at the top, embers at the bottom.
_FLAME = ["38;5;196", "38;5;196", "38;5;160", "38;5;160", "38;5;124"]

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")
_LEFT = "   "
_MIN_INNER = 48  # minimum info-box inner width

# The horned one, rising from the fog.
_EMBLEM = [
    "            ╲╲╲▖                               ▗╱╱╱",
    "              ╲╲╲╲▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄╱╱╱╱",
    "               ▐██▘   ◉               ◉   ▝██▌",
    "                ▝██▄▄        ╲▼╱        ▄▄██▘",
    "                   ▀▀██▄▄▄▄▄▄▄▄▄▄▄▄▄██▀▀",
]

# "PANDEMONIUM" in block letters (65 wide).
_WORDMARK = [
    "█████  ███  █   █ ████  █████ █   █  ███  █   █ █████ █   █ █   █",
    "█   █ █   █ ██  █ █   █ █     ██ ██ █   █ ██  █   █   █   █ ██ ██",
    "█████ █████ █ █ █ █   █ ███   █ █ █ █   █ █ █ █   █   █   █ █ █ █",
    "█     █   █ █  ██ █   █ █     █   █ █   █ █  ██   █   █   █ █   █",
    "█     █   █ █   █ ████  █████ █   █  ███  █   █ █████  ███  █   █",
]


def _c(text: str, code: str, on: bool) -> str:
    return f"\033[{code}m{text}{_RESET}" if on else text


def _strip(text: str) -> str:
    return _ANSI_RE.sub("", text)


def supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR") is not None:
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def _box(rows: list[tuple[str, str]], on: bool) -> list[str]:
    # Size the box to the longest line so nothing ever spills past the border.
    inner = max([_MIN_INNER] + [len(text) + 4 for text, _ in rows])
    top = _LEFT + _c("╔" + "═" * inner + "╗", _SMOKE, on)
    bot = _LEFT + _c("╚" + "═" * inner + "╝", _SMOKE, on)
    out = [top]
    for text, code in rows:
        body = f"  {text}".ljust(inner)
        out.append(_LEFT + _c("║", _SMOKE, on) + _c(body, code, on) + _c("║", _SMOKE, on))
    out.append(bot)
    return out


def render(version: str = "0.1.0", allowlist: str | None = None, color: bool | None = None) -> str:
    on = supports_color() if color is None else color

    lines: list[str] = [""]
    for row in _EMBLEM:
        if on:
            row = row.replace("◉", f"\033[{_EYE}m◉\033[{_FOG}m")
            lines.append(f"{_LEFT}\033[{_FOG}m{row}{_RESET}")
        else:
            lines.append(_LEFT + row)
    lines.append("")
    for row, code in zip(_WORDMARK, _FLAME):
        lines.append(_LEFT + _c(row, code, on))
    lines.append("")
    panel = [
        (f"the red agent  ·  CNC 418  ·  v{version}", _INK),
        ("lab-only · allowlist-enforced · verify-before-report", _INK2),
    ]
    if allowlist:
        panel.append((f"allowlist: {allowlist}", _INK2))
    lines += _box(panel, on)
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(render(color=True))
