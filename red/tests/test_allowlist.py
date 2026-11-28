"""Tests for the allowlist — the project's safety boundary.

These use IP literals and localhost so they run offline (no lab DNS needed).
Run with: python -m pytest   (or: python tests/run_tests.py)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pandemonium_red.allowlist import Allowlist, extract_host  # noqa: E402
from pandemonium_red.exceptions import TargetNotAllowedError  # noqa: E402


def lab_allowlist() -> Allowlist:
    return Allowlist.from_entries(
        entries=[
            "127.0.0.1/32",
            "172.16.10.0/24",  # DMZ
            "10.10.30.0/24",   # Servers
            "203.0.113.0/24",  # WAN edge
        ],
        hostnames=["web-01.lab"],
    )


def test_allows_lab_ips():
    al = lab_allowlist()
    assert al.is_allowed("127.0.0.1")
    assert al.is_allowed("172.16.10.10")
    assert al.is_allowed("10.10.30.20")
    assert al.is_allowed("203.0.113.5")


def test_denies_off_list():
    al = lab_allowlist()
    # real internet
    assert not al.is_allowed("8.8.8.8")
    # control plane, SOC, management — deliberately not listed
    assert not al.is_allowed("192.168.100.10")
    assert not al.is_allowed("10.10.40.10")
    assert not al.is_allowed("10.10.99.10")


def test_enforce_raises_on_refused():
    al = lab_allowlist()
    al.enforce("172.16.10.10")  # should not raise
    try:
        al.enforce("8.8.8.8")
    except TargetNotAllowedError as exc:
        assert exc.target == "8.8.8.8"
    else:  # pragma: no cover
        raise AssertionError("enforce did not raise on an off-list target")


def test_url_and_port_forms():
    al = lab_allowlist()
    assert al.is_allowed("http://172.16.10.10:3000/#/login")
    assert al.is_allowed("172.16.10.10:8080")
    assert not al.is_allowed("https://8.8.8.8/")
    assert not al.is_allowed("http://example.com")  # resolves outside the lab


def test_extract_host():
    assert extract_host("http://172.16.10.10:3000/x") == "172.16.10.10"
    assert extract_host("172.16.10.10:8080") == "172.16.10.10"
    assert extract_host("[::1]:8080") == "::1"
    assert extract_host("web-01.lab") == "web-01.lab"


def test_resolve_false_matches_names_literally():
    al = Allowlist.from_entries(hostnames=["web-01.lab"], resolve=False)
    assert al.is_allowed("web-01.lab")
    assert not al.is_allowed("app-01.lab")


if __name__ == "__main__":
    import traceback

    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"FAIL  {name}")
                traceback.print_exc()
    raise SystemExit(1 if failed else 0)
