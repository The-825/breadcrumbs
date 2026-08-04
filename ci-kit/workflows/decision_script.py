#!/usr/bin/env python3
"""Merge-decision logic for an agent-PR automerge gate. Second generation.

TEMPLATE. Copy to your workflow-scripts directory (conventionally
`.github/scripts/decision_script.py`) and edit the configuration block
below. Read AUTOMERGE_GOTCHAS.md first, especially "The second generation:
extract the decision, then graduate trust", which explains this file's
design and the maturity ladder it supports. The shipped `automerge.yml` in
this directory is the single-file starting point; this script is what that
workflow grows into when you add an operator label, protected paths, or
label-free lanes.

Pure functions. No network, no GitHub context, no side effects at import:
the workflow gathers the inputs (base branch, head branch, labels, draft
state, changed files, check runs, mergeable state) and calls this script;
unit tests (tests/test_decision_script.py) exercise the same functions
directly. That split is the point. The merge decision becomes testable
code instead of YAML conditionals, and every fail-closed guarantee below
is provable in a test instead of asserted in a comment.

Two phases, matching the two workflow steps that call this:

  lane   -> may this PR merge at all once checks are green?
            (branch lanes, draft guard, approval-label override,
            protected paths, content-policy lanes)
  checks -> are the checks and mergeable state good enough RIGHT NOW?
            (required checks green, nothing failing, zero-runs
            fail-closed, mergeable state clean)

Verdicts, printed as a trailing "verdict=..." line the workflow parses:

  merge -> proceed
  wait  -> do not merge, exit green; a later event (synchronize, labeled,
           ready_for_review, reopened) re-evaluates
  fail  -> a check is red; exit the job red so the failure is visible

THE ONE RULE THAT SHAPES THE PROTECTED LIST: a PR that edits its own merge
gate must never self-merge. Whatever else you trim from PROTECTED_PATHS,
the gate's own moving parts (this script, the automerge workflow, any
labeler workflows, the file that grants CI its token scopes) keep the
human gate. And the workflow must run the BASE branch's copy of this
script, so a PR's edit to the gate cannot influence its own gate run.

Calling shape, sketched (the gate step of your automerge workflow):

    # Check out the BASE branch: the trusted copy of this script. The
    # default pull_request checkout is the merge ref, i.e. PR content.
    - uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.base.ref }}
    - name: Merge gate
      run: |
        # A crash of this script must go RED, never read as merge=false.
        # See AUTOMERGE_GOTCHAS.md gotchas 8 and 9.
        set -o pipefail
        test -f .github/scripts/decision_script.py || {
          echo "decision script missing from the base branch; waiting loudly"
          exit 1
        }
        # Paginate the files listing and count renames as BOTH paths; on
        # any listing failure pass --files-error (gotcha 10, fail closed).
        gh api "repos/$REPO/pulls/$PR/files" --paginate \
          --jq '.[] | .filename, (.previous_filename // empty)' \
          > files.txt || FILES_ERR="--files-error"
        python3 .github/scripts/decision_script.py lane \
          --base "$BASE" --head "$HEAD" --labels-json "$LABELS_JSON" \
          --draft "$IS_DRAFT" --files-file files.txt ${FILES_ERR:-} \
          | tee lane_out.txt
        VERDICT=$(grep -o '^verdict=.*' lane_out.txt | cut -d= -f2)

The script itself exits 0 for every COMPUTED verdict ("wait" is a green
outcome: the PR is waiting, not broken), so pipefail only bites real
failures.

Fail-closed floor (all encoded below, all unit-tested, kept on EVERY rung
of the maturity ladder):
  * a DRAFT PR never merges;
  * ZERO check runs on the head SHA never merge (a missed event delivery
    must not become a silent merge);
  * a FAILING check never merges, and returns "fail" so the job goes red;
  * DIRTY or UNKNOWN mergeable state never merges;
  * an UNLISTABLE changed-file set never merges label-free (if you cannot
    see what changed, you cannot clear it);
  * a content-policy lane with no head/base tree to inspect never merges
    label-free.
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration. EDIT ME: every constant here is a convention to adapt.
# ---------------------------------------------------------------------------

# The only base branch this gate merges into. Everything else waits.
MAIN_BRANCH = "main"

# Branch namespaces eligible for automerge at all.
AGENT_PREFIXES = ("agent/",)

# The operator's release label. Its role depends on REQUIRE_LABEL: on rung
# one it is the gate (nothing merges without it); on rung two it is the
# universal override (a labeled PR skips the protected-path and
# content-policy checks). Placeholder on purpose; pick a short word your
# operator can type on a phone.
APPROVAL_LABEL = "<approval-label>"

# The maturity-ladder rung switch (AUTOMERGE_GOTCHAS.md, "second
# generation"). True = rung one: every merge is released by the operator's
# label. False = rung two: agent PRs self-merge on green unless they touch
# a protected path or fail a content policy. Which rung is right for your
# repo is an operator decision, not a default this kit can make for you.
# The kit ships rung one; graduate deliberately.
REQUIRE_LABEL = True

# Paths that keep the human gate even on the label-free rung. A trailing
# slash means "the whole tree"; no trailing slash means an exact file
# match. Machinery first: an agent PR that edits its own merge gate must
# never self-merge. Also keep high-blast-radius trees that have no CI
# policy lane (for example infrastructure-as-code with no plan step in PR
# context): a policy check that cannot run cannot fail closed.
PROTECTED_PATHS = [
    ".github/workflows/automerge.yml",
    ".github/scripts/decision_script.py",  # this file, at its deployed path
    # "<labeler-workflow>.yml",            # any workflow that applies APPROVAL_LABEL
    # "<ci-permissions-file>",             # whatever grants CI its token scopes
    # "<high-blast-radius-infra>/",        # e.g. your IaC tree, until it has a plan lane
]

# Check names that must be completed + success on the head SHA for every
# PR. Names match your checks workflow's job names. Matching is substring
# and case-insensitive because check-run names sometimes carry workflow
# prefixes or matrix suffixes.
ALWAYS_REQUIRED_CHECKS = ("Static checks", "E2E checks")

# Path-conditional checks: (name, relevance regex) pairs. The check is
# required only when a changed path matches its regex. The regex MUST
# mirror the producing workflow's `on.paths` filter exactly; when the two
# drift, a PR either merges without a check that should gate it or waits
# forever for a run that never comes. An unlistable file set makes every
# conditional check required (fail closed). Example:
#   CONDITIONAL_CHECKS = (("E2E checks", re.compile(r"^(static/|tests/e2e/)")),)
CONDITIONAL_CHECKS = ()

# Content-policy lanes: (path prefix, policy function) pairs. A path
# family may leave PROTECTED_PATHS only when a content lint replaces the
# judgment the label was buying. policy_fn(scoped_paths, head_root,
# base_root) returns a list of violation strings; any violation makes the
# PR wait for the label. See ci-kit/migrations/policy_checks.py for the
# worked example; wired it looks like:
#   from policy_checks import policy_violations
#   CONTENT_POLICIES = (("migrations/", policy_violations),)
CONTENT_POLICIES = ()

# ---------------------------------------------------------------------------
# Authority-ledger merge grants (Phase 2 of docs/authority-ledger.md; that
# doc is the contract, this block is the gate code it promised). A ledger
# line may carry the optional machine fields grant_type / applies_to /
# paths / until. When a PR body cites one (`Authority: G-YYYYMMDD-NN`),
# the citation can clear a WAIT at exactly two named sites in
# lane_decision, never a failing check and never a protected path:
#
#   applies_to="content-policy" -> the content-policy-violation wait, only
#       when EVERY changed file in the PR matches the grant's paths globs;
#   applies_to="promotion"      -> the non-agent-head wait for a head
#       branch listed in PROMOTION_HEADS, only while today (in
#       OPERATOR_TZ) is inside the grant's date..until window. A window
#       grant is the operator's standing release for that lane, so it
#       stands in for the approval label during the window.
#
# The ledger is read from the BASE branch checkout, never the PR head: a
# PR cannot mint or edit the grant that merges it. Free-text grants (no
# grant_type) never affect merging. Anything defective (unreadable
# ledger, malformed line, duplicate id, missing required field,
# unparseable date) evaluates as no-grant: the wait stands, the gate
# never crashes into a verdict.
# ---------------------------------------------------------------------------

# Where the ledger lives, relative to the BASE branch checkout root.
# EDIT ME to your ledger's path (the pattern doc suggests one per repo).
LEDGER_REL_PATH = "AUTHORITY_LEDGER.jsonl"

# Head branches whose PRs are promotion merges (e.g. a staging branch
# promoting into main; see docs/staging-promotion.md). Empty tuple =
# promotion-window grants are inert. EDIT ME, e.g. ("staging",).
PROMOTION_HEADS = ()

# Grant windows are dated in the operator's timezone. EDIT ME.
OPERATOR_TZ = "America/Los_Angeles"
OPERATOR_TZ_FALLBACK_UTC_OFFSET = -8  # standard offset; a window can never open early

GRANT_CITATION_RE = re.compile(r"Authority:\s*(G-\d{8}-\d{2})")
GRANT_ID_RE = re.compile(r"^G-\d{8}-\d{2}$")
MERGE_GRANT_TYPE = "merge-authority"
GRANT_CONTENT_POLICY = "content-policy"
GRANT_PROMOTION = "promotion"

# Check-run conclusions that block a merge outright.
FAILING_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}

# This gate's own job appears as a check run on the same SHA; a failed
# earlier attempt must not deadlock the next one. Match your job name.
SELF_CHECK_RE = re.compile(r"squash merge|auto-?merge", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Phase one: the lane decision.
# ---------------------------------------------------------------------------

def is_protected(path, protected=None):
    """True when path is on the protected list (exact file, or inside a
    trailing-slash tree entry)."""
    protected = PROTECTED_PATHS if protected is None else protected
    for p in protected:
        if p.endswith("/"):
            if path.startswith(p):
                return True
        elif path == p:
            return True
    return False


def load_grants(ledger_path):
    """Grants by id from the base branch's ledger. ANY defect in the file
    (unreadable, a non-JSON or non-object line, a malformed or duplicate
    id) discards the WHOLE ledger: {} means no grants and the wait
    stands."""
    grants = {}
    try:
        with open(ledger_path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if not isinstance(entry, dict):
                    return {}
                gid = entry.get("id")
                if not isinstance(gid, str) or not GRANT_ID_RE.match(gid) \
                        or gid in grants:
                    return {}
                grants[gid] = entry
    except Exception:
        return {}
    return grants


def parse_citations(pr_body):
    """Ordered, deduplicated Authority citations from a PR body."""
    out = []
    for gid in GRANT_CITATION_RE.findall(pr_body or ""):
        if gid not in out:
            out.append(gid)
    return out


def _parse_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def today_operator_tz():
    """Today in OPERATOR_TZ (grant windows are dated there). The no-tzdata
    fallback uses the configured standard offset, so a window can never
    open early through the fallback."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo(OPERATOR_TZ)).date()
    except Exception:
        return (datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=OPERATOR_TZ_FALLBACK_UTC_OFFSET)).date()


def grant_clears_wait(kind, entry, files, today, protected=None):
    """May this one grant clear a wait of `kind` for this file set? Every
    branch answers False unless the grant affirmatively covers the PR.
    Protected paths are never grant-overridable: machinery keeps the
    human gate regardless of any citation."""
    if files is None:
        return False
    if any(is_protected(f, protected) for f in files):
        return False
    if entry.get("status") != "active":
        return False
    if entry.get("grant_type") != MERGE_GRANT_TYPE:
        return False
    if entry.get("applies_to") != kind:
        return False
    expiry = entry.get("expiry")
    if expiry is not None:
        expiry_date = _parse_date(expiry)
        if expiry_date is None or today > expiry_date:
            return False
    until = entry.get("until")
    until_date = _parse_date(until) if until is not None else None
    if until is not None and until_date is None:
        return False
    if until_date is not None and today > until_date:
        return False
    if kind == GRANT_PROMOTION:
        start = _parse_date(entry.get("date"))
        # A promotion grant is a dated window: both ends required.
        if start is None or until_date is None:
            return False
        return start <= today
    if kind == GRANT_CONTENT_POLICY:
        globs = entry.get("paths")
        if not isinstance(globs, list) or not globs or \
                not all(isinstance(g, str) and g for g in globs):
            return False
        return all(any(fnmatch.fnmatchcase(f, g) for g in globs)
                   for f in files)
    return False


def grant_clearance(kind, pr_body, files, base_root, today=None,
                    ledger_rel_path=None, protected=None):
    """First cited grant that validly clears a wait of `kind`.
    Returns (grant_id, scope_text), or (None, None) when no citation
    qualifies (which leaves the wait exactly as it was)."""
    ledger_rel_path = LEDGER_REL_PATH if ledger_rel_path is None else ledger_rel_path
    citations = parse_citations(pr_body)
    if not citations or base_root is None:
        return None, None
    grants = load_grants(os.path.join(base_root, ledger_rel_path))
    if not grants:
        return None, None
    if today is None:
        today = today_operator_tz()
    for gid in citations:
        entry = grants.get(gid)
        if entry is not None and grant_clears_wait(kind, entry, files, today,
                                                  protected=protected):
            return gid, _grant_scope_text(kind, entry)
    return None, None


def _grant_scope_text(kind, entry):
    """Human-readable scope for the audit line; kept parenthesis-free so
    the full audit text stays machine-extractable from the reason."""
    if kind == GRANT_PROMOTION:
        return "promotion window %s..%s" % (entry.get("date"), entry.get("until"))
    return "%s, paths %s" % (GRANT_CONTENT_POLICY,
                             ", ".join(entry.get("paths") or []))


def grant_audit_text(gid, scope):
    """The exact audit string carried in the decision reason and posted as
    the PR comment when a grant clears a wait."""
    return "Merged under Authority: %s (scope: %s)" % (gid, scope)


def lane_decision(base, head, labels, draft, files,
                  head_root=None, base_root=None,
                  require_label=None, content_policies=None, protected=None,
                  pr_body=None, today=None,
                  promotion_heads=None, ledger_rel_path=None):
    """May this PR merge at all once checks are green?

    files is the changed-path list (renames contribute BOTH paths), or
    None when the listing failed: every label-free decision then fails
    closed. head_root/base_root are filesystem checkouts of the PR head
    and the base branch, consumed by content policies and the authority
    ledger; None when unavailable (fail closed for any PR a content
    policy covers, and no grants). pr_body is the PR description, scanned
    for `Authority: G-...` citations; None consults no grants. today is a
    date override for tests.

    Returns (verdict, reason) with verdict in {"merge", "wait"}.
    """
    require_label = REQUIRE_LABEL if require_label is None else require_label
    content_policies = CONTENT_POLICIES if content_policies is None else content_policies
    promotion_heads = PROMOTION_HEADS if promotion_heads is None else promotion_heads

    def grant_for(kind):
        return grant_clearance(kind, pr_body, files, base_root, today=today,
                               ledger_rel_path=ledger_rel_path,
                               protected=protected)

    if draft:
        return "wait", "draft PR; automerge never merges drafts"
    if base != MAIN_BRANCH:
        return "wait", f"base branch {base!r} is not {MAIN_BRANCH!r}; not this gate's business"
    if not head.startswith(AGENT_PREFIXES):
        if head in promotion_heads:
            if APPROVAL_LABEL in labels:
                return "merge", "promotion lane: approval label present, explicit operator release"
            gid, scope = grant_for(GRANT_PROMOTION)
            if gid:
                return "merge", ("promotion lane cleared by grant; "
                                 + grant_audit_text(gid, scope))
            return "wait", (f"promotion head {head!r}: waiting for the approval label "
                            "or a valid promotion-window grant citation")
        return "wait", f"head branch {head!r} is not an agent branch; not this gate's business"
    if APPROVAL_LABEL in labels:
        # The operator's explicit release. It overrides protected paths and
        # content policies (and a failed file listing): the human looked.
        return "merge", "approval label present: explicit operator release, merges on green"
    if require_label:
        return "wait", "rung one: every merge is released by the approval label; waiting"

    # Label-free rung. From here, every decision needs the file list.
    if files is None:
        return "wait", "could not list changed files; failing closed, PR waits for the label"
    hits = sorted({f for f in files if is_protected(f, protected)})
    if hits:
        return "wait", "protected paths require the approval label: " + ", ".join(hits)
    for prefix, policy in content_policies:
        scoped = sorted({f for f in files if f.startswith(prefix)})
        if not scoped:
            continue
        if head_root is None or base_root is None:
            return "wait", (f"changed files under {prefix} but no head/base checkout for "
                            "the content policy; failing closed, PR waits for the label")
        violations = policy(scoped, head_root, base_root)
        if violations:
            gid, scope = grant_for(GRANT_CONTENT_POLICY)
            if gid:
                return "merge", ("content-policy wait cleared by grant; "
                                 + grant_audit_text(gid, scope))
            return "wait", ("content-policy violations require the approval label: "
                            + "; ".join(violations))
    return "merge", "label-free rung: no protected paths, content policies clean, merges on green"


# ---------------------------------------------------------------------------
# Phase two: the checks decision.
# ---------------------------------------------------------------------------

def latest_runs_per_name(checks):
    """Collapse duplicate check runs to the newest run per check name.

    A push that fires duplicate workflow events leaves the superseded run's
    conclusion (usually `cancelled`) permanently attached to the head SHA
    alongside the superseding run's `success` of the SAME check name. The
    platform's "latest" filter does not save you: duplicate events create
    separate check suites, and the filter collapses within a suite, not
    across them. Without this dedup the SHA is poisoned forever and only an
    empty-commit re-fire unblocks it. Check-run ids are assigned in creation
    order, so the newest run per name is the max `id`. Runs without an
    integer id cannot be ordered; they are ALL kept, preserving the
    pre-dedup fail-closed behavior for payloads that lack the field.
    """
    latest = {}
    unordered = []
    for c in checks:
        cid = c.get("id")
        if not isinstance(cid, int):
            unordered.append(c)
            continue
        name = c.get("name") or ""
        prev = latest.get(name)
        if prev is None or cid > prev["id"]:
            latest[name] = c
    return unordered + list(latest.values())


def checks_decision(checks, merge_state, files=None,
                    always_required=None, conditional=None):
    """Are the checks and mergeable state good enough to merge RIGHT NOW?

    checks: list of {"id", "name", "status", "conclusion"} dicts for the
    head SHA (`id` may be absent in older payloads; see
    latest_runs_per_name). merge_state: the platform's mergeable-state
    string (CLEAN, DIRTY, UNKNOWN, ...). files: changed paths, or None
    when the listing failed (which makes every conditional check required,
    fail closed).

    Returns (verdict, reason) with verdict in {"merge", "wait", "fail"}.
    """
    always_required = ALWAYS_REQUIRED_CHECKS if always_required is None else always_required
    conditional = CONDITIONAL_CHECKS if conditional is None else conditional

    checks = [c for c in checks if not SELF_CHECK_RE.search(c.get("name") or "")]
    if not checks:
        return "wait", "zero check runs for this SHA; failing closed (no merge without CI evidence)"
    checks = latest_runs_per_name(checks)

    for c in checks:
        if c.get("status") == "completed" and (c.get("conclusion") or "") in FAILING_CONCLUSIONS:
            return "fail", f"check failing: {c.get('name')} = {c.get('conclusion')}"

    def runs_matching(name):
        needle = name.lower()
        return [c for c in checks if needle in (c.get("name") or "").lower()]

    required = [(name, runs_matching(name)) for name in always_required]
    for name, relevance in conditional:
        if files is None or any(relevance.match(f) for f in files):
            required.append((name, runs_matching(name)))
    for name, runs in required:
        if not runs:
            return "wait", f"required check {name!r} has no run yet for this SHA"
        if not any(c.get("status") == "completed" and c.get("conclusion") == "success"
                   for c in runs):
            return "wait", f"required check {name!r} is not green yet"

    ms = (merge_state or "").upper()
    if ms == "DIRTY":
        return "wait", "merge conflict (mergeable state DIRTY); resolve on the feature branch"
    if ms in ("", "UNKNOWN"):
        return "wait", "mergeable state UNKNOWN; not merging until the platform reports it"
    return "merge", f"required checks green, nothing failing, mergeable state {ms}"


# ---------------------------------------------------------------------------
# CLI: the workflow-facing contract.
# ---------------------------------------------------------------------------

def _read_files_arg(args):
    """None means the listing failed or was not provided (fail closed)."""
    if args.files_error or not args.files_file:
        return None
    with open(args.files_file, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="automerge decision gate (see the module docstring)")
    sub = ap.add_subparsers(dest="phase", required=True)

    lane = sub.add_parser("lane", help="branch lane + label + protected paths + content policy")
    lane.add_argument("--base", required=True)
    lane.add_argument("--head", required=True)
    lane.add_argument("--labels-json", required=True, help="JSON array of label names")
    lane.add_argument("--draft", required=True, choices=["true", "false"])
    lane.add_argument("--files-file", help="newline-separated changed paths")
    lane.add_argument("--files-error", action="store_true",
                      help="the file listing failed; fail closed")
    lane.add_argument("--head-root", help="checkout of the PR head (content-policy file contents)")
    lane.add_argument("--base-root", help="checkout of the base branch (the trusted tree)")
    lane.add_argument("--pr-body-file",
                      help="file holding the PR body, scanned for Authority: G-... "
                           "citations (omit to consult no grants)")

    checks = sub.add_parser("checks", help="check runs + mergeable state")
    checks.add_argument("--checks-json-file", required=True,
                        help='path to a JSON array of {"id","name","status","conclusion"};'
                             ' id optional but enables duplicate-run dedup')
    checks.add_argument("--merge-state", required=True)
    checks.add_argument("--files-file", help="newline-separated changed paths")
    checks.add_argument("--files-error", action="store_true")

    args = ap.parse_args(argv)

    if args.phase == "lane":
        pr_body = None
        if getattr(args, "pr_body_file", None):
            try:
                with open(args.pr_body_file, "r", encoding="utf-8") as fh:
                    pr_body = fh.read()
            except OSError:
                pr_body = None  # unreadable body consults no grants; waits stand
        verdict, reason = lane_decision(
            args.base, args.head, json.loads(args.labels_json),
            args.draft == "true", _read_files_arg(args),
            head_root=args.head_root, base_root=args.base_root,
            pr_body=pr_body)
    else:
        with open(args.checks_json_file, "r", encoding="utf-8") as fh:
            check_runs = json.load(fh)
        verdict, reason = checks_decision(check_runs, args.merge_state,
                                          _read_files_arg(args))

    # Exit 0 for every computed verdict: "wait" is a green outcome (the PR
    # is waiting, not broken). Only real crashes exit non-zero, and the
    # calling step's pipefail turns those red instead of silent.
    print(f"reason: {reason}")
    print(f"verdict={verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
