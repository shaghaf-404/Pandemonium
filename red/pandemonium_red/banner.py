cat > pandemonium_red/banner.py << 'PANDEMO_EOF'
"""The Pandemonium console banner (ASCII art, shown on launch)."""
from __future__ import annotations

import os
import re
import sys

_RESET = "\033[0m"
_BOLD = "\033[1m"
_FOG = "38;5;250"     # pale mist
_SMOKE = "38;5;243"   # grey
_MUTE = "38;5;240"    # dim grey
_EYE = "38;5;196"     # glowing red
# Flame gradient for the wordmark, bright at the top, embers at the bottom.
_FLAME = ["38;5;196", "38;5;196", "38;5;160", "38;5;160", "38;5;124"]

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")
_LEFT = "   "

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

_INNER = 62  # info-box inner width


def _c(text: str, code: str, on: bool) -> str:
    return f"\033[{code}m{text}{_RESET}" if on else text


def _strip(text: str) -> str:
    return _ANSI_RE.sub("", text)


def supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR") is not None:
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def _box(lines: list[str], on: bool) -> list[str]:
    top = _LEFT + _c("╔" + "═" * _INNER + "╗", _SMOKE, on)
    bot = _LEFT + _c("╚" + "═" * _INNER + "╝", _SMOKE, on)
    out = [top]
    for text, code in lines:
        body = f"  {text}".ljust(_INNER)
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
        (f"the red agent  ·  CNC 418  ·  v{version}", _FOG),
        ("lab-only · allowlist-enforced · verify-before-report", _MUTE),
    ]
    if allowlist:
        panel.append((f"allowlist: {allowlist}", _MUTE))
    lines += _box(panel, on)
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(render(color=True))
PANDEMO_EOF
