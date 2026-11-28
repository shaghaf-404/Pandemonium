"""Pandemonium Red — the AI-driven offensive agent (CNC 418).

Public surface kept small on purpose; the allowlist is the one thing every
other part depends on.
"""
from __future__ import annotations

from .allowlist import Allowlist
from .exceptions import PandemoniumRedError, TargetNotAllowedError
from .executor import DryRunExecutor, Executor, ToolResult
from .findings import ChainStep, Finding, new_id
from .verify import Verifier, VerifierRegistry

__all__ = [
    "Allowlist",
    "PandemoniumRedError",
    "TargetNotAllowedError",
    "Executor",
    "DryRunExecutor",
    "ToolResult",
    "Finding",
    "ChainStep",
    "new_id",
    "Verifier",
    "VerifierRegistry",
]

__version__ = "0.1.0"
