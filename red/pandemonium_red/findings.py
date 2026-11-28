"""The finding data model — the contract Red shares with Blue and GRC.

A finding is only ever reported after the verifier confirms it, so
``exploit_status`` and ``verified_poc`` are the trustworthy fields. The
fields follow the CNC 418 cross-course schema, and a multi-step attack is
represented explicitly as an ordered ``chain`` rather than one flat record.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

EXPLOIT_STATUS = ("unverified", "verified", "failed", "rejected")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "find") -> str:
    """A short unique id, e.g. ``find-1a2b3c4d``."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@dataclass
class ChainStep:
    """One step in a multi-step attack chain."""

    order: int
    target: str
    technique: str  # MITRE technique id or a short name
    description: str = ""
    evidence: str = ""  # what proved this step worked

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Finding:
    """A single verified (or pending) finding."""

    target_asset: str
    title: str
    finding_id: str = field(default_factory=lambda: new_id())
    exercise_run_id: str = ""
    cwe_id: str | None = None
    stride_category: str | None = None
    mitre_technique_id: str | None = None
    cvss_vector: str | None = None
    exploit_status: str = "unverified"
    verified_poc: str = ""  # reproducible evidence, filled by the verifier
    chain: list[ChainStep] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if self.exploit_status not in EXPLOIT_STATUS:
            raise ValueError(
                f"exploit_status must be one of {EXPLOIT_STATUS}, got {self.exploit_status!r}"
            )

    # --- serialization -------------------------------------------------
    def to_dict(self) -> dict:
        data = asdict(self)
        data["chain"] = [step.to_dict() for step in self.chain]
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_sarif(self) -> dict:
        """Wrap this finding as a minimal SARIF 2.1.0 log (one result)."""
        level = "error" if self.exploit_status == "verified" else "warning"
        return {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {"driver": {"name": "Pandemonium-Red", "rules": []}},
                    "results": [
                        {
                            "ruleId": self.mitre_technique_id or self.cwe_id or "finding",
                            "level": level,
                            "message": {"text": self.title},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": self.target_asset}
                                    }
                                }
                            ],
                            "properties": {
                                "finding_id": self.finding_id,
                                "exercise_run_id": self.exercise_run_id,
                                "exploit_status": self.exploit_status,
                                "cwe_id": self.cwe_id,
                                "stride_category": self.stride_category,
                                "cvss_vector": self.cvss_vector,
                                "verified_poc": self.verified_poc,
                                "chain": [step.to_dict() for step in self.chain],
                            },
                        }
                    ],
                }
            ],
        }

    @property
    def is_verified(self) -> bool:
        return self.exploit_status == "verified"
