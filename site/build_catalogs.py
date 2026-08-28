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
    horizons = {"longitudinal": 0, "repeated": 1, "single": 2, "technical": 3, "retrospective": 4, "not observed": 5}
    output = []
    for source_id, source, level, finding, impact, boundary in ledger:
        app = appraisals[source_id]
        title, url = source_link(source)
        output.append({
            "id": source_id, "title": title, "url": url, "levelEvidence": level,
            "finding": finding, "impact": impact.replace("**", ""), "boundary": boundary,
            "design": app[1], "directness": app[2], "family": app[3], "horizon": app[4],
            "flags": app[5], "claims": [x.strip() for x in app[6].split(",") if x.strip()],
            "_sort": [proximity.get(app[2][:2], 9), horizons.get(app[4], 9), int(source_id)],
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
    for rank, item in enumerate(output, 1):
        item["popularityOrder"] = rank
    return output


def write(name: str, value: object) -> None:
    target = SITE / "data" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write("research.json", research_catalog())
    write("repositories.json", repository_catalog())
