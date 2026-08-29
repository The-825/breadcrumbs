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
    family_labels = {
        "AGENT-EVAL": "Agent evaluation", "AGENT-SCALE": "Large-scale agent systems", "AGENT-SECURITY": "Agent security",
        "ALGO-USE": "Algorithm use and reliance", "ALLOCATION": "Task allocation", "AUTO-HF": "Automation and human factors",
        "BANSAL-TEAM": "Human-AI team performance", "CLINICAL-TEAM": "Clinical team collaboration", "DEFER": "Learning when to defer",
        "DELEGATION": "Delegation", "DEV-PROD": "Developer productivity", "FAIRNESS-HCAI": "Fairness and human-centered AI",
        "FEEDBACK-LOOP": "Feedback loops", "FIELD-PROD": "Field productivity", "FIELD-TEAM": "Field team performance",
        "JOINT-ACTIVITY": "Joint activity", "MEM-ARCH": "Memory architecture", "MEM-EVAL": "Memory evaluation",
        "MOTIVATION": "Motivation", "MSR-AGENTS": "Microsoft Research agent studies", "MSR-WORK": "Microsoft Research work-practice studies",
        "MULTIAGENT": "Multi-agent systems", "ORG-SYN": "Organizational synthesis", "PORTFOLIO-DIVERSITY": "Portfolio diversity",
        "RELIANCE-FRICTION": "Reliance and friction", "RETRIEVAL": "Retrieval", "SELF-REFINE": "Self-refinement",
        "SYNERGY-META": "Collaboration synergy meta-analysis", "TEAM-COG": "Team cognition", "TRUST-REL": "Trust and reliance",
        "XAI-BEHAVIOR": "Explainability and behavior", "XAI-GUIDANCE": "Explainability guidance",
    }
    output = []
    for source_id, source, level, finding, impact, boundary in ledger:
        app = appraisals[source_id]
        title, url = source_link(source)
        claims = [x.strip() for x in app[6].split(",") if x.strip()]
        output.append({
            "id": source_id, "title": title, "url": url, "levelEvidence": level,
            "finding": finding, "impact": impact.replace("**", ""), "boundary": boundary,
            "design": app[1], "directness": app[2], "directnessValue": int(app[2][1]),
            "family": app[3], "familyLabel": family_labels.get(app[3], app[3]), "horizon": app[4], "horizonValue": horizon_value.get(app[4], 0),
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
    output.sort(key=lambda item: (item["stars_observed"] is None, -(item["stars_observed"] or 0), item["repository"]))
    category_counts: dict[str, int] = {}
    for rank, item in enumerate(output, 1):
        item["catalogOrder"] = rank
        item["popularityOrder"] = rank if item["stars_observed"] is not None else None
        category = item["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
        item["categoryPopularityOrder"] = category_counts[category] if item["stars_observed"] is not None else None
        item["visibleMechanisms"] = sum(value == "V" for value in item["mechanisms"].values())
        item["partialMechanisms"] = sum(value == "P" for value in item["mechanisms"].values())
        item["unknownMechanisms"] = sum(value == "U" for value in item["mechanisms"].values())
        item["mechanismTotal"] = len(item["mechanisms"])
        item["claimCount"] = len(item["claims"])
        item["lastReviewed"] = item["snapshot_date"]
        item["starsObservedDate"] = item.get("stars_observed_date") or landscape["popularity_observed_date"]
        item["ledgerRepositoryCount"] = len(output)
        item["detailedReviewCount"] = sum(row["evidence_depth"] != "source-assessment" for row in output)
    totals: dict[str, int] = {}
    for item in output:
        totals[item["category"]] = totals.get(item["category"], 0) + 1
    for item in output:
        item["categoryRepositoryCount"] = totals[item["category"]]
    return output


def claim_catalog() -> list[dict[str, str]]:
    text = (DOCS / "collaborative-intelligence-claim-register.md").read_text(encoding="utf-8")
    themes = {
        "CI-001": "Outcomes and burden", "CI-004": "Outcomes and burden", "CI-005": "Outcomes and burden", "CI-015": "Outcomes and burden", "CI-016": "Outcomes and burden",
        "CI-002": "Workflow evidence", "CI-006": "Workflow evidence", "CI-008": "Workflow evidence", "CI-017": "Workflow evidence",
        "CI-003": "Authority and reliance", "CI-007": "Authority and reliance", "CI-011": "Authority and reliance", "CI-012": "Authority and reliance", "CI-013": "Authority and reliance",
        "CI-009": "Memory and grounding", "CI-010": "Memory and grounding", "CI-014": "Memory and grounding",
    }
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
            "id": match.group(1), "title": match.group(2), "theme": themes.get(match.group(1), "Other"),
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
