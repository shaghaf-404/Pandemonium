"""Hard-coded target allowlist for the Pandemonium Red agent.

Every target the agent is about to touch MUST pass through ``enforce()``.
The policy is **default-deny**: anything not explicitly allowed is refused.

This is the project's safety boundary. It keeps the exercise inside the lab:
the Red agent may attack the lab "company" (DMZ, Users, Servers) but can never
reach the real internet, the university network, the SOC, the management
network, or the out-of-band control plane. It is required by the CNC 418 brief
and is part of the grade.

Note: this allowlist (what Red is allowed to attack) is a *different thing*
from the Blue team's blocklist (whose traffic the firewall drops during the
game). This one is static and lives in our code; the blocklist is dynamic and
lives in the firewall.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .exceptions import TargetNotAllowedError

IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network
IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


def extract_host(target: str) -> str:
    """Pull a hostname or IP out of a raw host, a ``host:port``, or a URL."""
    target = target.strip()
    if not target:
        raise TargetNotAllowedError(target, "empty target")
    if "://" in target:
        host = urlparse(target).hostname
        if not host:
            raise TargetNotAllowedError(target, "could not parse a host from the URL")
        return host
    if target.startswith("["):  # bracketed IPv6, e.g. [::1]:8080
        return target[1:].split("]", 1)[0]
    if target.count(":") == 1:  # host:port
        return target.split(":", 1)[0]
    return target


def resolve_ips(host: str) -> list[IPAddress]:
    """Resolve a hostname to every IP it points at.

    An IP literal resolves to itself. A hostname that does not resolve is
    treated as not allowed (we refuse what we cannot pin to an IP).
    """
    try:
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise TargetNotAllowedError(host, f"could not resolve host: {exc}") from exc
    ips: list[IPAddress] = []
    for info in infos:
        addr = info[4][0].split("%", 1)[0]  # drop any IPv6 scope id
        ips.append(ipaddress.ip_address(addr))
    return ips


@dataclass
class Allowlist:
    """A default-deny allowlist of lab networks and hostnames."""

    networks: list[IPNetwork] = field(default_factory=list)
    hostnames: set[str] = field(default_factory=set)
    resolve: bool = True  # resolve hostnames and check their IPs, not just the name

    @classmethod
    def from_entries(
        cls,
        entries: list[str] | None = None,
        hostnames: list[str] | None = None,
        resolve: bool = True,
    ) -> "Allowlist":
        """Build an allowlist from a mixed list of CIDRs/IPs plus hostnames.

        Anything that parses as a network goes to ``networks``; everything
        else is treated as a hostname.
        """
        networks: list[IPNetwork] = []
        hosts = {h.strip().lower() for h in (hostnames or [])}
        for entry in entries or []:
            text = str(entry).strip()
            if not text:
                continue
            try:
                networks.append(ipaddress.ip_network(text, strict=False))
            except ValueError:
                hosts.add(text.lower())
        return cls(networks=networks, hostnames=hosts, resolve=resolve)

    def _ip_allowed(self, ip: IPAddress) -> bool:
        return any(ip in net for net in self.networks)

    def check(self, target: str) -> str:
        """Return the host if the target is allowed, else raise.

        A raw IP is allowed when it falls inside an allowed network. A
        hostname is allowed when every IP it resolves to falls inside an
        allowed network (so a lab name pointing at a lab subnet passes, but a
        name that resolves outside the lab is refused). With ``resolve=False``
        a hostname is allowed only if it is explicitly listed.
        """
        host = extract_host(target)

        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            ip = None

        if ip is not None:
            if self._ip_allowed(ip):
                return host
            raise TargetNotAllowedError(target, f"IP {host} is outside every allowed network")

        if not self.resolve:
            if host.lower() in self.hostnames:
                return host
            raise TargetNotAllowedError(target, "hostname not in allowlist (resolution disabled)")

        ips = resolve_ips(host)
        outside = [str(i) for i in ips if not self._ip_allowed(i)]
        if outside:
            raise TargetNotAllowedError(
                target, f"host resolves outside the lab: {', '.join(outside)}"
            )
        return host

    def is_allowed(self, target: str) -> bool:
        """Boolean form of :meth:`check` — never raises."""
        try:
            self.check(target)
            return True
        except TargetNotAllowedError:
            return False

    def enforce(self, target: str) -> str:
        """The single choke point. Call this before ANY action on a target.

        Returns the host on success; raises :class:`TargetNotAllowedError`
        otherwise. Every executor runs this first, so there is exactly one
        place where "may I touch this?" is decided.
        """
        return self.check(target)
