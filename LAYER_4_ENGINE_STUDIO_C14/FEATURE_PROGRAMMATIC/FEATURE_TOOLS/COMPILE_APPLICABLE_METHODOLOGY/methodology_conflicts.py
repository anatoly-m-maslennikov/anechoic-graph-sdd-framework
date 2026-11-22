"""Identify conflicts and deterministic frontier records for Methodology candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_candidate import Candidate


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def candidate_sort_key(candidate: Candidate) -> tuple[object, ...]:
    return (candidate.layer_order, candidate.atom_id, candidate.version, candidate.source_path)


def proposal_sort_key(candidate: Candidate) -> tuple[object, ...]:
    priority_rank = priority_value(candidate.priority)
    return (-candidate.version, -priority_rank, candidate.layer_order, candidate.source_path)


def priority_value(value: str | None) -> int:
    if value is None:
        return 0
    labels = {"low": 10, "medium": 20, "high": 30, "critical": 40}
    if value.lower() in labels:
        return labels[value.lower()]
    try:
        return int(value)
    except ValueError:
        return 0


def frontier_digest(candidates: Iterable[Candidate]) -> str:
    records = [candidate.frontier_record() for candidate in sorted(candidates, key=candidate_sort_key)]
    return sha256_bytes(canonical_json(records))


def conflict_record(kind: str, candidates: Iterable[Candidate], proposal: Candidate, **details: object) -> dict[str, object]:
    ordered = sorted(set(candidates), key=candidate_sort_key)
    identity = {
        "type": kind,
        "candidate_source_carrier_paths": [candidate.source_path for candidate in ordered],
        "details": details,
    }
    return {
        "conflict_id": sha256_bytes(canonical_json(identity)),
        "type": kind,
        "candidate_source_carrier_paths": identity["candidate_source_carrier_paths"],
        "details": details,
        "proposed_resolution": {"selected_source_carrier_path": proposal.source_path},
    }


def candidate_aliases(candidate: Candidate) -> set[str]:
    stem = Path(candidate.basename).stem
    return {candidate.atom_id, stem, stem.split("--", 1)[0]}


def _identity_conflicts(conflicts, by_identity, by_definition_term, involved_pairs, involved_priority):
    for atom_id, group in sorted(by_identity.items()):
        if len(group) <= 1:
            continue
        group_paths = {candidate.source_path for candidate in group}
        if any(pair.issubset(group_paths) for pair in involved_pairs) or group_paths.intersection(involved_priority):
            continue
        proposal = sorted(group, key=proposal_sort_key)[0]
        conflicts.append(conflict_record("duplicate_selected_atom_identity", group, proposal, atom_id=atom_id))

    for (namespace, term), group in sorted(by_definition_term.items()):
        if len(group) <= 1:
            continue
        group_paths = {candidate.source_path for candidate in group}
        if any(pair.issubset(group_paths) for pair in involved_pairs) or group_paths.intersection(involved_priority):
            continue
        proposal = sorted(group, key=proposal_sort_key)[0]
        conflicts.append(
            conflict_record(
                "duplicate_governed_term_definition",
                group,
                proposal,
                term=f"{namespace} <+ Term//{term}" if namespace else term,
                definition_namespace=namespace,
                definition_term_name=term,
                definition_subject_paths={
                    candidate.source_path: candidate.definition_subject_path
                    for candidate in sorted(group, key=candidate_sort_key)
                },
            )
        )


def _relation_conflicts(conflicts, replacement_pairs, incompatibility_pairs, lookup):
    for replacer_path, replaced_path in sorted(replacement_pairs):
        replacer = lookup[replacer_path]
        replaced = lookup[replaced_path]
        conflicts.append(
            conflict_record(
                "unresolved_replacement",
                (replacer, replaced),
                replacer,
                replacer_source_carrier_path=replacer_path,
                replaced_source_carrier_path=replaced_path,
            )
        )

    for first_path, second_path in sorted(incompatibility_pairs):
        group = (lookup[first_path], lookup[second_path])
        proposal = sorted(group, key=proposal_sort_key)[0]
        conflicts.append(conflict_record("incompatible_retained_candidates", group, proposal))


def _group_conflicts(conflicts, by_priority_group, by_output):
    for group_name, group in sorted(by_priority_group.items()):
        if len(group) <= 1:
            continue
        proposal = sorted(group, key=proposal_sort_key)[0]
        conflicts.append(
            conflict_record(
                "unresolved_priority",
                group,
                proposal,
                priority_group=group_name,
                observed_priorities={candidate.source_path: candidate.priority for candidate in sorted(group, key=candidate_sort_key)},
            )
        )

    for (role_directory, basename), group in sorted(by_output.items()):
        if len(group) <= 1:
            continue
        proposal = sorted(group, key=proposal_sort_key)[0]
        conflicts.append(
            conflict_record(
                "output_path_collision",
                group,
                proposal,
                output_path=f"{group[0].output_relative}/{role_directory}/{basename}",
            )
        )


def detect_conflicts(candidates: list[Candidate]) -> list[dict[str, object]]:
    conflicts: list[dict[str, object]] = []
    by_identity: dict[str, list[Candidate]] = {}
    alias_index: dict[str, list[Candidate]] = {}
    by_output: dict[tuple[str, str], list[Candidate]] = {}
    by_priority_group: dict[str, list[Candidate]] = {}
    by_definition_term: dict[tuple[str, str], list[Candidate]] = {}
    for candidate in candidates:
        by_identity.setdefault(candidate.atom_id, []).append(candidate)
        by_output.setdefault((candidate.role_directory, candidate.basename), []).append(candidate)
        if candidate.priority_group:
            by_priority_group.setdefault(candidate.priority_group, []).append(candidate)
        if candidate.definition_term:
            by_definition_term.setdefault((candidate.definition_namespace, candidate.definition_term), []).append(candidate)
        for alias in candidate_aliases(candidate):
            alias_index.setdefault(alias, []).append(candidate)

    replacement_pairs: set[tuple[str, str]] = set()
    incompatibility_pairs: set[tuple[str, str]] = set()
    for candidate in candidates:
        for target in candidate.replacements:
            for replaced in alias_index.get(target, []):
                if replaced.source_path != candidate.source_path:
                    replacement_pairs.add((candidate.source_path, replaced.source_path))
        for target in candidate.incompatibilities:
            for incompatible in alias_index.get(target, []):
                if incompatible.source_path != candidate.source_path:
                    incompatibility_pairs.add(tuple(sorted((candidate.source_path, incompatible.source_path))))

    lookup = {candidate.source_path: candidate for candidate in candidates}
    involved_pairs = {frozenset(pair) for pair in replacement_pairs}.union(frozenset(pair) for pair in incompatibility_pairs)
    involved_priority = {candidate.source_path for group in by_priority_group.values() if len(group) > 1 for candidate in group}

    _identity_conflicts(conflicts, by_identity, by_definition_term, involved_pairs, involved_priority)
    _relation_conflicts(conflicts, replacement_pairs, incompatibility_pairs, lookup)
    _group_conflicts(conflicts, by_priority_group, by_output)

    conflicts.sort(key=lambda item: (str(item["type"]), str(item["conflict_id"])))
    return conflicts
