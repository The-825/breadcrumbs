#!/usr/bin/env python3
"""Trusted-principal scope gate for the runnable memory engine.

ASSUMES the host application already authenticates callers and can provide the
current principal through a trusted adapter. The request never supplies a
principal, audience, role, or clearance. This module maps the host-resolved
principal to one fixed memory audience and calls MemoryEngine.build_context.

This is an authorization seam, not an authentication server. Copy it beside
memory_engine.py, implement PrincipalProvider with your host's verified session
or workload identity, and keep that provider outside model-controlled input.
"""
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol

from memory_engine import MAX_EPISODES_IN_CONTEXT, MemoryEngine


SCOPES = frozenset(("public", "internal", "regulated"))


class PrincipalProvider(Protocol):
    """Host-owned adapter that returns the already-authenticated principal."""

    def current_principal(self) -> str:
        ...


@dataclass(frozen=True)
class ScopePolicy:
    """Immutable principal-to-clearance policy loaded by the trusted host."""

    grants: Mapping[str, str]

    def __post_init__(self) -> None:
        normalized = {}
        for principal, scope in self.grants.items():
            principal_id = str(principal).strip()
            if not principal_id:
                raise ValueError("scope policy refuses an empty principal")
            if scope not in SCOPES:
                raise ValueError(
                    f"unknown scope {scope!r}: use public, internal, or regulated"
                )
            normalized[principal_id] = scope
        object.__setattr__(self, "grants", normalized)

    def clearance_for(self, principal: str) -> str:
        principal_id = str(principal).strip()
        if not principal_id or principal_id not in self.grants:
            raise PermissionError("authenticated principal has no memory scope grant")
        return self.grants[principal_id]


class ScopedContextService:
    """Build memory context without accepting caller-asserted scope."""

    def __init__(self, engine: MemoryEngine, principal_provider: PrincipalProvider,
                 policy: ScopePolicy):
        self._engine = engine
        self._principal_provider = principal_provider
        self._policy = policy

    def build_context(self, query="", max_episodes=MAX_EPISODES_IN_CONTEXT,
                      as_of=None, valid_at=None):
        principal = self._principal_provider.current_principal()
        audience = self._policy.clearance_for(principal)
        return self._engine.build_context(
            query=query,
            max_episodes=max_episodes,
            as_of=as_of,
            valid_at=valid_at,
            audience=audience,
        )


class _FixturePrincipalProvider:
    def __init__(self, principal):
        self.principal = principal

    def current_principal(self):
        return self.principal


def selftest():
    checks = []

    def ok(name, condition):
        checks.append((name, bool(condition)))

    with tempfile.TemporaryDirectory(prefix="scoped_context_") as tmp:
        engine = MemoryEngine(Path(tmp))
        engine.store_fact("kit", "license", "MIT", scope="public")
        engine.store_fact("ops", "runbook", "internal steps", scope="internal")
        engine.store_fact("records", "case", "regulated detail", scope="regulated")
        policy = ScopePolicy({
            "anonymous-web": "public",
            "staff-session": "internal",
            "records-worker": "regulated",
        })

        public = ScopedContextService(
            engine, _FixturePrincipalProvider("anonymous-web"), policy
        ).build_context()
        ok("public principal cannot see internal or regulated facts",
           "MIT" in public and "internal steps" not in public
           and "regulated detail" not in public)

        internal = ScopedContextService(
            engine, _FixturePrincipalProvider("staff-session"), policy
        ).build_context()
        ok("internal principal cannot see regulated facts",
           "MIT" in internal and "internal steps" in internal
           and "regulated detail" not in internal)

        regulated = ScopedContextService(
            engine, _FixturePrincipalProvider("records-worker"), policy
        ).build_context()
        ok("regulated principal receives its policy clearance",
           "MIT" in regulated and "internal steps" in regulated
           and "regulated detail" in regulated)

        unknown_refused = False
        try:
            ScopedContextService(
                engine, _FixturePrincipalProvider("unlisted-caller"), policy
            ).build_context()
        except PermissionError:
            unknown_refused = True
        ok("an authenticated but ungranted principal fails closed", unknown_refused)

        widening_refused = False
        public_service = ScopedContextService(
            engine, _FixturePrincipalProvider("anonymous-web"), policy
        )
        try:
            public_service.build_context(audience="regulated")
        except TypeError:
            widening_refused = True
        ok("a request cannot assert or widen its audience", widening_refused)

        invalid_policy_refused = False
        try:
            ScopePolicy({"caller": "superuser"})
        except ValueError:
            invalid_policy_refused = True
        ok("the trusted policy refuses an unknown clearance", invalid_policy_refused)

    failed = [name for name, passed in checks if not passed]
    for name, passed in checks:
        print(f"  {'ok  ' if passed else 'FAIL'} {name}")
    print(f"scoped_context selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    raise SystemExit(selftest() if args.selftest else parser.print_help())
