"""The verification layer — anti-hallucination.

A finding is only trusted when a ``Verifier`` confirms it *programmatically*
(an out-of-band callback, a boolean/time inference, an out-of-band listener),
never because a model said so. This file defines the interface and a registry;
the concrete checks per vulnerability class are built in later steps.

This is the highest-value graded piece, so it is deliberately its own layer,
separate from the LLM that proposes findings.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .executor import Executor
from .findings import Finding


class Verifier(ABC):
    """Confirms (or rejects) one class of finding with deterministic evidence."""

    name: str = "verifier"

    @abstractmethod
    def applies_to(self, finding: Finding) -> bool:
        """Whether this verifier knows how to check this finding."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, finding: Finding, executor: Executor) -> bool:
        """Return True and set ``finding.verified_poc`` on success."""
        raise NotImplementedError


class VerifierRegistry:
    """Routes a finding to the first verifier that applies to it."""

    def __init__(self) -> None:
        self._verifiers: list[Verifier] = []

    def register(self, verifier: Verifier) -> None:
        self._verifiers.append(verifier)

    def verify(self, finding: Finding, executor: Executor) -> Finding:
        """Run the matching verifier and stamp the finding's status.

        No verifier for this finding → it stays ``unverified`` and is never
        reported as real. A verifier that fails → ``rejected``.
        """
        for verifier in self._verifiers:
            if verifier.applies_to(finding):
                ok = verifier.verify(finding, executor)
                finding.exploit_status = "verified" if ok else "rejected"
                return finding
        finding.exploit_status = "unverified"
        return finding


# TODO (step 2+): concrete verifiers, e.g. a reflected-input check confirmed by
# a headless-browser callback, blind SQLi confirmed by boolean/time inference,
# blind SSRF confirmed by an out-of-band listener. Each sets verified_poc to
# reproducible evidence.
