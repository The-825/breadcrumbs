#!/usr/bin/env python3
"""Attach a published Breadcrumb Score pointer to a public A2A Agent Card."""
from __future__ import annotations
import argparse, copy, hashlib, ipaddress, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

EXTENSION_URI = "https://github.com/The-825/breadcrumbs/extensions/score/v1"
REQUIRED_CARD_FIELDS = {"name", "description", "supportedInterfaces", "version", "capabilities", "defaultInputModes", "defaultOutputModes", "skills"}
ALLOWED_CARD_FIELDS = REQUIRED_CARD_FIELDS | {"provider", "documentationUrl", "securitySchemes", "securityRequirements", "signatures", "iconUrl"}
class ExportError(ValueError): pass

def _time(value: str) -> datetime:
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc: raise ExportError("invalid ISO timestamp") from exc
    if parsed.tzinfo is None: raise ExportError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)

def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _public_url(value: str, field: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname: raise ExportError(f"{field} must be an absolute HTTPS URL")
    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith(".local"): raise ExportError(f"{field} must not expose a local endpoint")
    try: address = ipaddress.ip_address(host)
    except ValueError: return
    if not address.is_global: raise ExportError(f"{field} must use a public endpoint")

def validate_card(card: Mapping[str, Any]) -> None:
    missing = REQUIRED_CARD_FIELDS - set(card)
    if missing: raise ExportError(f"missing Agent Card fields: {', '.join(sorted(missing))}")
    unknown = set(card) - ALLOWED_CARD_FIELDS
    if unknown: raise ExportError(f"unknown public Agent Card fields: {', '.join(sorted(unknown))}")
    if card.get("signatures"): raise ExportError("a signed Agent Card must be re-signed by its provider after extension")
    if not isinstance(card.get("capabilities"), Mapping): raise ExportError("capabilities must be an object")
    interfaces = card.get("supportedInterfaces")
    if not isinstance(interfaces, list) or not interfaces: raise ExportError("supportedInterfaces must be a non-empty list")
    for index, interface in enumerate(interfaces):
        if not isinstance(interface, Mapping): raise ExportError(f"supportedInterfaces[{index}] must be an object")
        for field in ("url", "protocolBinding", "protocolVersion"):
            if not isinstance(interface.get(field), str) or not interface[field].strip(): raise ExportError(f"supportedInterfaces[{index}].{field} is required")
        if interface["protocolBinding"] in {"JSONRPC", "HTTP+JSON"}: _public_url(interface["url"], f"supportedInterfaces[{index}].url")

def attach_score(card: Mapping[str, Any], assessment: Mapping[str, Any], result: Mapping[str, Any], evidence_url: str, expires_at: str, now: str) -> dict[str, Any]:
    validate_card(card); _public_url(evidence_url, "evidence_url")
    if assessment.get("status") != "published" or assessment.get("human_reviewed") is not True or not assessment.get("publication_approval"): raise ExportError("assessment must be published, human reviewed, and publication approved")
    if assessment.get("target", {}).get("name") != card.get("name"): raise ExportError("assessment target does not match Agent Card name")
    digest = _digest(assessment)
    if result.get("assessment_digest") != digest: raise ExportError("assessment digest does not match result")
    if result.get("target") != card.get("name") or result.get("status") != "published": raise ExportError("score result does not match the published target")
    if _time(expires_at) <= _time(now): raise ExportError("assessment is expired")
    extension = {"uri": EXTENSION_URI, "description": "Links to an evidence-scoped readiness assessment.", "required": False, "params": {"evidenceUrl": evidence_url, "assessmentDigest": digest, "evaluatorVersion": result.get("evaluator_version"), "assessedAt": assessment.get("assessed_at"), "expiresAt": expires_at, "status": "published", "evidenceCoverage": result.get("evidence_coverage"), "readinessBand": result.get("readiness_band")}}
    output = copy.deepcopy(dict(card)); capabilities = dict(output["capabilities"])
    capabilities["extensions"] = [x for x in capabilities.get("extensions", []) if x.get("uri") != EXTENSION_URI] + [extension]
    output["capabilities"] = capabilities
    return output

def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("card", type=Path); parser.add_argument("assessment", type=Path); parser.add_argument("result", type=Path)
    parser.add_argument("--evidence-url", required=True); parser.add_argument("--expires-at", required=True); parser.add_argument("--now", required=True); parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try: exported = attach_score(json.loads(args.card.read_text()), json.loads(args.assessment.read_text()), json.loads(args.result.read_text()), args.evidence_url, args.expires_at, args.now)
    except (OSError, json.JSONDecodeError, ExportError) as exc: parser.error(str(exc))
    rendered = json.dumps(exported, indent=2, sort_keys=True) + "\n"
    if args.output: args.output.write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return 0
if __name__ == "__main__": raise SystemExit(main())
