#!/usr/bin/env -S python3 -B
"""Prepare, but never apply, the Header-group reference migration."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PLAN = ROOT / ".anechoic_anechoic/02_analysis/draft/header-groups-20261106"
SNAPSHOT = PLAN / "native-snapshot.json"
OUT = Path(__file__).with_name("impact.json")

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.assets.content_declaration_schema.reference_impact_patterns import (
    COMMON, ROLE_FIELDS, ALL_FIELDS, DIRECT_ATOM, DIRECT_VAR, DIRECT_ROLE, RELATIVE,
    ROLE_QUALIFIED, ATOM_CONTEXT, ATOM_ROLE, ATOM_BINDING, TYPED_ATOM, SUMMARY,
    E240_BARE, BARE_COMMON, BARE_COMMON_PATHS, E240_PATHS,
)


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def protected_summary_spans(text):
    spans = []
    for match in SUMMARY.finditer(text):
        next_heading = re.search(r"(?m)^## (?!#)", text[match.end() :])
        spans.append((match.start(), match.end() + next_heading.start() if next_heading else len(text)))
    return spans


def in_spans(position, spans):
    return any(start <= position < end for start, end in spans)


def summary_texts(text):
    return [text[start:end] for start, end in protected_summary_spans(text)]


def frontmatter(text):
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[: end + 5] if end >= 0 else ""


def protected_metadata(text):
    header = frontmatter(text)
    fields = re.findall(r"(?m)^(?:atom_id|ref_id|status|version|updated_at):[^\n]*$", header)
    relations = re.search(r"(?ms)^relations:\n(?:^[ \t].*(?:\n|$))*", header)
    return fields, relations.group(0) if relations else ""


def atom_bindings(text):
    """Return Atom variables and their proven role, if the source binds one."""
    bindings = {}
    for match in ATOM_BINDING.finditer(text):
        bindings[match.group("var")] = match.group("role") or (
            match.group("root") if match.group("root") in ROLE_FIELDS else None
        )
    for match in TYPED_ATOM.finditer(text):
        bindings.setdefault(match.group("var"), None)
    return bindings


def replacement(field, role=None):
    if field in COMMON:
        return COMMON[field]
    if role in ROLE_FIELDS and field in ROLE_FIELDS[role]:
        return f"Context.{role}.{field}"
    return None


def _rewrite_direct(text, bindings, replace_match):
    def direct_atom(match):
        mapped = replacement(match.group("field"))
        return f"Atom.Header.{mapped}" if mapped else None

    result = replace_match(DIRECT_ATOM, text, direct_atom, "direct_atom")

    def direct_var(match):
        role = bindings.get(match.group("var"))
        if match.group("var") not in bindings:
            return None
        mapped = replacement(match.group("field"), role)
        return f"{match.group('var')}.Header.{mapped}" if mapped else None

    result = replace_match(DIRECT_VAR, result, direct_var, "typed_atom")

    def direct_role(match):
        mapped = replacement(match.group("field"), match.group("role"))
        return f"{match.group('role')}.Header.{mapped}" if mapped else None

    result = replace_match(DIRECT_ROLE, result, direct_role, "role_root")

    def role_qualified(match):
        mapped = replacement(match.group("field"), match.group("role"))
        return f"{match.group('role')}/(.Header.{mapped}" if mapped else None

    result = replace_match(ROLE_QUALIFIED, result, role_qualified, "role_qualified")

    return result


def _rewrite_relative(result, counts):
    pieces = []
    offset = 0
    for statement in re.split(r"(;)", result):
        statement_start = offset
        offset += len(statement)
        if statement == ";" or not ATOM_CONTEXT.search(statement):
            pieces.append(statement)
            continue
        role_match = ATOM_ROLE.search(statement)
        role = role_match.group("role") if role_match else None

        def qualified(match):
            absolute = statement_start + match.start()
            if in_spans(absolute, protected_summary_spans(result)):
                return match.group(0)
            mapped = replacement(match.group("field"), role)
            if mapped is None:
                return match.group(0)
            counts["qualified_atom"] += 1
            counts[match.group("field")] += 1
            return f".Header.{mapped}"

        pieces.append(RELATIVE.sub(qualified, statement))
    result = "".join(pieces)

    return result


def _find_holds(result, bindings):
    holds = []
    def add_hold(match, reason):
        if in_spans(match.start(), protected_summary_spans(result)):
            return
        line_start = result.rfind("\n", 0, match.start()) + 1
        line_end = result.find("\n", match.end())
        holds.append(
            {
                "token": match.group(0),
                "reason": reason,
                "snippet": result[line_start : len(result) if line_end < 0 else line_end].strip(),
            }
        )

    for match in DIRECT_ATOM.finditer(result):
        if match.group("field") not in COMMON:
            add_hold(match, "role_specific_atom_header_has_no_proven_role")
    for match in DIRECT_VAR.finditer(result):
        field = match.group("field")
        role = bindings.get(match.group("var"))
        if match.group("var") not in bindings:
            add_hold(match, "variable_is_not_proven_Atom")
        elif field not in COMMON and replacement(field, role) is None:
            add_hold(match, "role_specific_atom_header_has_no_proven_matching_role")
    for match in DIRECT_ROLE.finditer(result):
        add_hold(match, "role_property_is_not_an_approved_existing_contract")
    for match in ROLE_QUALIFIED.finditer(result):
        add_hold(match, "role_property_is_not_an_approved_existing_contract")

    return holds


def migrate(text, path=None):
    """Return proposed text, replacement counts, actual holds, and skipped refs."""
    counts = Counter()
    bindings = atom_bindings(text)
    summary_skips = 0

    def replace_match(pattern, source, make_replacement, kind):
        nonlocal summary_skips
        chunks = []
        last = 0
        source_protected = protected_summary_spans(source)
        for match in pattern.finditer(source):
            chunks.append(source[last : match.start()])
            if in_spans(match.start(), source_protected):
                chunks.append(match.group(0))
                summary_skips += 1
            else:
                new = make_replacement(match)
                if new is None:
                    chunks.append(match.group(0))
                else:
                    chunks.append(new)
                    counts[kind] += 1
                    counts[match.group("field")] += 1
            last = match.end()
        chunks.append(source[last:])
        return "".join(chunks)

    result = _rewrite_direct(text, bindings, replace_match)

    result = _rewrite_relative(result, counts)

    if path in E240_PATHS:
        result = replace_match(
            E240_BARE,
            result,
            lambda match: "Header.Context.Topics.Main Subject",
            "known_e240_bare_atom",
        )

    if path in BARE_COMMON_PATHS:
        result = replace_match(
            BARE_COMMON,
            result,
            lambda match: f"Header.{replacement(match.group('field'))}",
            "known_reviewed_bare_atom",
        )

    holds = _find_holds(result, bindings)

    return result, counts, holds, summary_skips


def transform(text, path=None):
    """Pure, idempotent full-carrier transform; path enables only known E240 prose."""
    return migrate(text, path)[0]


def rewrite(path, text):
    """Composer interface: use the full carrier path and full carrier text."""
    return transform(text, path)


def self_check():
    assert replacement("Ref ID") == "Identity.Ref ID"
    assert replacement("RefID") == "Identity.RefID"
    assert replacement("Updated At") == "State.Updated At"
    assert replacement("UpdatedAt") == "State.UpdatedAt"
    assert replacement("Subjects") == "Context.Topics"
    assert replacement("Subjects.Active") == "Context.Topics.Main Subject"
    assert replacement("Subjects.Passive") == "Context.Topics.Dependencies"
    assert replacement("Priority", "Concern") == "Context.Concern.Priority"
    assert replacement("Priority", "Plan") is None
    text = "Atom/(.Header.Role: Plan)/(.Header.Form: X);"
    after, _, holds, _ = migrate(text)
    assert after == "Atom/(.Header.Context.Role: Plan)/(.Header.Context.Form: X);" and not holds
    typed = "Atom/(.Header.Role: Plan)//$atom; $atom.Header.Work Sequence Number"
    after, _, holds, _ = migrate(typed)
    assert "$atom.Header.Context.Plan.Work Sequence Number" in after and not holds
    assert transform(after) == after
    role, _, holds, _ = migrate("Atom/(.Header.Role: Concern).Header.Priority;")
    assert role == "Atom/(.Header.Context.Role: Concern).Header.Context.Concern.Priority;" and not holds
    relative, _, holds, _ = migrate("UNIQUE(Atom//$atom, (.Header.ID, .Header.Version));")
    assert "(.Header.Identity.ID, .Header.State.Version)" in relative and not holds
    subject, _, holds, _ = migrate("Atom//$atom; $atom.Header.Subjects.Passive")
    assert "$atom.Header.Context.Topics.Dependencies" in subject and not holds
    bare = "Header.Subjects.Active"
    assert transform(bare) == bare
    assert rewrite(next(iter(E240_PATHS)), bare) == "Header.Context.Topics.Main Subject"
    reviewed_path = next(iter(BARE_COMMON_PATHS))
    assert rewrite(reviewed_path, "Header.Container") == "Header.Context.Container"
    assert rewrite(reviewed_path, "Entity.Header.ID") == "Entity.Header.ID"
    assert transform("Header.Container") == "Header.Container"
    sql_columns = "header_context_plan header_context_plan_work_sequence_number"
    assert transform(sql_columns) == sql_columns
    unchanged, _, holds, _ = migrate("Atom.Header.Context.Role Entity.Header.ID Entity.Header.Status")
    assert unchanged == "Atom.Header.Context.Role Entity.Header.ID Entity.Header.Status" and not holds


def _validated_snapshot():
    snapshot = json.loads(SNAPSHOT.read_text())
    carriers = snapshot["carriers"]
    expected_count = snapshot["expected_count"]
    baseline_source_count = snapshot["baseline_source_count"]
    supplemental_sources = snapshot.get("supplemental_sources", [])
    assert len(carriers) == expected_count
    assert len({row["path"] for row in carriers}) == expected_count
    assert expected_count == baseline_source_count + len(supplemental_sources)
    assert {
        (row["path"], row["sha256"]) for row in supplemental_sources
    } <= {(row["path"], row["sha256"]) for row in carriers}
    return carriers, supplemental_sources


def main():
    self_check()
    carriers, supplemental_sources = _validated_snapshot()
    operations = []
    holds = []
    counts = Counter(native_current_draft_carriers=len(carriers))
    snapshot_hash_mismatches = 0

    for row in carriers:
        path = row["path"]
        before = (ROOT / path).read_text()
        before_hash = sha256(before)
        if before_hash != row["sha256"]:
            snapshot_hash_mismatches += 1
        after, local_counts, local_holds, summary_skips = migrate(before, path)
        after_check, _, after_holds, _ = migrate(after, path)
        assert after_check == after and not after_holds
        assert summary_texts(before) == summary_texts(after)
        assert protected_metadata(before) == protected_metadata(after)
        counts.update(local_counts)
        counts["summary_references_skipped"] += summary_skips
        for hold in local_holds:
            holds.append({"path": path, **hold})
        if before != after:
            counts["idempotent_operations"] += 1
            operations.append(
                {
                    "path": path,
                    "before": before,
                    "after": after,
                    "before_sha256": before_hash,
                    "after_sha256": sha256(after),
                }
            )

    counts["operations"] = len(operations)
    counts["reference_spans"] = sum(counts[field] for field in ALL_FIELDS)
    counts["snapshot_hash_mismatches"] = snapshot_hash_mismatches
    counts["supplemental_sources"] = len(supplemental_sources)
    plan = {"operations": operations, "holds": holds, "counts": dict(sorted(counts.items()))}
    OUT.write_text(json.dumps(plan, indent=2) + "\n")
    print(json.dumps({"operations": len(operations), "holds": len(holds), "counts": plan["counts"]}, indent=2))


if __name__ == "__main__":
    main()
