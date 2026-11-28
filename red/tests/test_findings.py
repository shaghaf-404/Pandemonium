"""Tests for the finding model and its JSON / SARIF serialization."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pandemonium_red.findings import ChainStep, Finding  # noqa: E402


def test_finding_defaults_and_json():
    f = Finding(target_asset="172.16.10.10", title="Reflected input observed")
    assert f.finding_id.startswith("find-")
    assert f.exploit_status == "unverified"
    assert not f.is_verified
    data = json.loads(f.to_json())
    for key in ("finding_id", "exercise_run_id", "target_asset", "title", "exploit_status"):
        assert key in data


def test_invalid_status_rejected():
    try:
        Finding(target_asset="x", title="y", exploit_status="totally-exploited")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("invalid exploit_status was accepted")


def test_chain_serializes():
    f = Finding(
        target_asset="10.10.30.20",
        title="Chain to the database host",
        exercise_run_id="run-001",
        chain=[
            ChainStep(order=1, target="172.16.10.10", technique="T1190", description="entry"),
            ChainStep(order=2, target="10.10.30.20", technique="T1210", description="pivot"),
        ],
    )
    data = f.to_dict()
    assert len(data["chain"]) == 2
    assert data["chain"][0]["order"] == 1


def test_sarif_shape():
    f = Finding(
        target_asset="172.16.10.10",
        title="Verified issue",
        exercise_run_id="run-002",
        exploit_status="verified",
        verified_poc="out-of-band callback received",
    )
    sarif = f.to_sarif()
    assert sarif["version"] == "2.1.0"
    result = sarif["runs"][0]["results"][0]
    assert result["level"] == "error"
    assert result["properties"]["exercise_run_id"] == "run-002"
    assert result["properties"]["verified_poc"]


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
