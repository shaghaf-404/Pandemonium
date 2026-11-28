"""The execution layer — the only place a tool is run against a target.

The allowlist is enforced in ``Executor.run`` so that every tool call passes
through one choke point. HexStrike (MIT-licensed) will plug in here later as a
concrete ``Executor`` that drives the real kali tools over MCP; we reuse its
*execution* plumbing, not its decision engine. Nothing in this file runs an
attack yet — ``DryRunExecutor`` only reports what *would* run.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .allowlist import Allowlist


@dataclass
class ToolResult:
    """The structured result of running one tool against one target."""

    tool: str
    target: str
    ok: bool = True
    raw: str = ""
    structured: dict = field(default_factory=dict)


class Executor(ABC):
    """Base executor. Enforces the allowlist before delegating to ``_run``."""

    def __init__(self, allowlist: Allowlist) -> None:
        self.allowlist = allowlist

    def run(self, tool: str, target: str, **kwargs) -> ToolResult:
        # The choke point: refuse anything outside the allowlist, always.
        self.allowlist.enforce(target)
        return self._run(tool, target, **kwargs)

    @abstractmethod
    def _run(self, tool: str, target: str, **kwargs) -> ToolResult:
        """Actually run the tool. Implemented by concrete executors."""
        raise NotImplementedError


class DryRunExecutor(Executor):
    """Safe default: logs what it would run, touches nothing.

    Use this until HexStrike is wired in, and in tests, so the pipeline can be
    exercised end to end without sending a single packet.
    """

    def __init__(self, allowlist: Allowlist) -> None:
        super().__init__(allowlist)
        self.calls: list[ToolResult] = []

    def _run(self, tool: str, target: str, **kwargs) -> ToolResult:
        result = ToolResult(
            tool=tool,
            target=target,
            ok=True,
            raw=f"[dry-run] would run {tool} against {target} with {kwargs}",
            structured={"dry_run": True, "args": kwargs},
        )
        self.calls.append(result)
        return result


# TODO (step 1): class HexStrikeExecutor(Executor) — call the HexStrike MCP /
# HTTP API, map our tool name + target to its request, parse the response into
# ToolResult.structured. The allowlist still runs first, in the base class.
