"""The Pandemonium console banner (ASCII art, shown on launch)."""
from __future__ import annotations

import os
import re
import sys

# ANSI colors (256-color). Stripped automatically when output isn't a terminal.
_RESET = "\033[0m"
_BOLD = "\033[1m"
_FOG = "\033[38;5;250m"    # pale grey mist
_SMOKE = "\033[38;5;243m"  # darker grey
_EYE = "\033[38;5;196m"    # glowing red
_ACCENT = "\033[38;5;160m"  # blood red
_MUTE = "\033[38;5;240m"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

# The horned one, rising from the fog.
_EMBLEM = [
    "         ╲╲╲                             ╱╱╱",
    "          ╲╲╲╲                         ╱╱╱╱",
    "           ╲╲╲╲╲                     ╱╱╱╱╱",
    "            ╲╲╲╲▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖╱╱╱╱",
    "                ▐                 ▌",
    "                ▐   ◉         ◉   ▌",
    "                ▐       ╲╳╱       ▌",
    "                ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘",
]

_NAME = "P A N D E M O N I U M"
_BORDER_TOP = "   ┌" + "─" * 47 + "┐"
_BORDER_BOT = "   └" + "─" * 47 + "┘"


def _strip(text: str) -> str:
    return _ANSI_RE.sub("", text)


def supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR") is not None:
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def render(version: str = "0.1.0", allowlist: str | None = None, color: bool | None = None) -> str:
    if color is None:
        color = supports_color()

    lines: list[str] = [""]
    for row in _EMBLEM:
        row = row.replace("◉", f"{_EYE}◉{_FOG}")
        lines.append(f"{_FOG}{row}{_RESET}")
    lines.append("")

    # Wordmark box (inner width 47).
    pad = 47 - len(_NAME) - 8
    lines.append(f"{_SMOKE}{_BORDER_TOP}{_RESET}")
    lines.append(
        f"{_SMOKE}   │        {_BOLD}{_ACCENT}{_NAME}{_RESET}{_SMOKE}{' ' * pad}│{_RESET}"
    )
    lines.append(f"{_SMOKE}{_BORDER_BOT}{_RESET}")
    lines.append("")

    lines.append(f"   {_FOG}red · CNC 418{_RESET}   {_MUTE}·{_RESET}   {_FOG}v{version}{_RESET}")
    lines.append(f"   {_MUTE}lab-only · allowlist-enforced · verify-before-report{_RESET}")
    if allowlist:
        lines.append(f"   {_MUTE}allowlist: {allowlist}{_RESET}")
    lines.append("")

    out = "\n".join(lines)
    return out if color else _strip(out)


if __name__ == "__main__":
    print(render(color=True))
