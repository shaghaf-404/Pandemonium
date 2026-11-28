"""Exceptions for the Pandemonium Red agent."""
from __future__ import annotations


class PandemoniumRedError(Exception):
    """Base class for every error raised by the Red agent."""


class TargetNotAllowedError(PandemoniumRedError):
    """Raised when a target is not permitted by the allowlist.

    This is the hard safety boundary of the whole project: if it is raised,
    nothing was sent to the target. It is caught and logged, never bypassed.
    """

    def __init__(self, target: str, reason: str = "") -> None:
        self.target = target
        self.reason = reason
        message = f"Target refused by allowlist: {target!r}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)
