"""Load the allowlist (and later, agent settings) from a config file.

Supports JSON out of the box (stdlib). YAML is supported too if PyYAML is
installed; the example ships as YAML because it reads nicely, but a ``.json``
file works with no extra dependency.
"""
from __future__ import annotations

import json
from pathlib import Path

from .allowlist import Allowlist


def _load_mapping(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # optional dependency
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError(
                f"{path} is YAML but PyYAML is not installed. "
                "Run `pip install pyyaml`, or use a .json allowlist instead."
            ) from exc
        return yaml.safe_load(text) or {}
    return json.loads(text)


def load_allowlist(path: str | Path) -> Allowlist:
    """Build an :class:`Allowlist` from a YAML or JSON config file.

    Expected keys: ``networks`` (list of CIDRs/IPs), ``hostnames`` (list),
    and optional ``resolve`` (bool, default True).
    """
    path = Path(path)
    data = _load_mapping(path)
    return Allowlist.from_entries(
        entries=data.get("networks", []),
        hostnames=data.get("hostnames", []),
        resolve=bool(data.get("resolve", True)),
    )
