from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"


def table_rows(path: Path, width: int) -> list[list[str]]:
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == width and cells[0] not in {"ID", "---"}:
            found.append(cells)
    return found


def source_link(value: str) -> tuple[str, str]:
    match = re.search(r'\["([^"]+)"\]\((https?://[^)]+)\)', value)
    return (match.group(1), match.group(2)) if match else (value, "")


def research_catalog() -> list[dict[str, object]]:
    ledger = table_rows(DOCS / "collaborative-intelligence-research-ledger.md", 6)
    appraisals = {row[0]: row for row in table_rows(DOCS / "collaborative-intelligence-source-appraisals.md", 7)}
    proximity = {"D3": 0, "D2": 1, "D1": 2, "D0": 3}
    horizon_order = {"longitudinal": 0, "repeated": 1, "single": 2, "technical": 3, "retrospective": 4, "not observed": 5}
    horizon_value = {"longitudinal": 3, "repeated": 2, "single": 1, "technical": 1, "retrospective": 1, "not observed": 0}
    output = []
    for source_id, source, level, finding, impact, boundary in ledger:
        app = appraisals[source_id]
        title, url = source_link(source)
        claims = [x.strip() for x in app[6].split(",") if x.strip()]
        output.append({
            "id": source_id, "title": title, "url": url, "levelEvidence": level,
            "finding": finding, "impact": impact.replace("**", ""), "boundary": boundary,
            "design": app[1], "directness": app[2], "directnessValue": int(app[2][1]),
            "family": app[3], "horizon": app[4], "horizonValue": horizon_value.get(app[4], 0),
            "flags": app[5], "claims": claims, "claimCount": len(claims),
            "citationSignal": "not collected",
            "_sort": [proximity.get(app[2][:2], 9), horizon_order.get(app[4], 9), int(source_id)],
        })
    output.sort(key=lambda item: item["_sort"])
    for rank, item in enumerate(output, 1):
        item["evidenceOrder"] = rank
        del item["_sort"]
    return output


def repository_catalog() -> list[dict[str, object]]:
    landscape = json.loads((DOCS / "collaborative-intelligence-repository-landscape.json").read_text(encoding="utf-8"))
    output = landscape["repositories"]
    output.sort(key=lambda item: (-item["stars_observed"], item["repository"]))
    aspect_counts: dict[str, int] = {}
    for rank, item in enumerate(output, 1):
        item["popularityOrder"] = rank
        aspect = item["selection_aspect"]
        aspect_counts[aspect] = aspect_counts.get(aspect, 0) + 1
        item["aspectPopularityOrder"] = aspect_counts[aspect]
        item["visibleMechanisms"] = sum(value == "V" for value in item["mechanisms"].values())
        item["partialMechanisms"] = sum(value == "P" for value in item["mechanisms"].values())
        item["mechanismTotal"] = len(item["mechanisms"])
        item["claimCount"] = len(item["claims"])
        item["lastReviewed"] = item["snapshot_date"]
        item["starsObservedDate"] = landscape["popularity_observed_date"]
    totals: dict[str, int] = {}
    for item in output:
        totals[item["selection_aspect"]] = totals.get(item["selection_aspect"], 0) + 1
    for item in output:
        item["aspectRepositoryCount"] = totals[item["selection_aspect"]]
    return output


def claim_catalog() -> list[dict[str, str]]:
    text = (DOCS / "collaborative-intelligence-claim-register.md").read_text(encoding="utf-8")
    output = []
    for section in re.split(r"^### ", text, flags=re.MULTILINE)[1:]:
        heading, body = section.split("\n", 1)
        match = re.match(r"(CI-\d+):\s*(.+)", heading)
        if not match:
            continue
        def field(label: str) -> str:
            found = re.search(rf"^- \*\*{re.escape(label)}:\*\*\s*(.+(?:\n  .+)*)", body, flags=re.MULTILINE)
            return " ".join(found.group(1).split()) if found else ""
        claim = re.search(r"\*\*Claim\.\*\*\s*(.*?)(?=\n\n- \*\*)", body, flags=re.DOTALL)
        output.append({
            "id": match.group(1), "title": match.group(2),
            "claim": " ".join(claim.group(1).split()) if claim else "",
            "supports": field("Supports"), "profile": field("Profile"),
            "disposition": field("Disposition").replace("`", ""),
            "nullCase": field("Null case"), "nextTest": field("Next test"),
        })
    return output


def write(name: str, value: object) -> None:
    target = SITE / "data" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write("research.json", research_catalog())
    write("repositories.json", repository_catalog())
    write("claims.json", claim_catalog())
