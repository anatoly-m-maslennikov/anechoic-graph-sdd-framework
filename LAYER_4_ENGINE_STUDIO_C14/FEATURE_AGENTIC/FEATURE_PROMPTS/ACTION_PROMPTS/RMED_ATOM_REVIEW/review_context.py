"""Validate and retain caller-bound review context."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from typing import Any, TypeGuard

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.relation_ordering import validate_ordering_policy
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.context_builder import (authority_reference, metadata, validated_candidate_bindings,
                             validated_principle_admissions, validate_baseline_sources)


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())



def probability(value: Any) -> TypeGuard[float | int]:
    return (type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 1)



def strings(value: Any, *, empty: bool = False) -> bool:
    return isinstance(value, list) and (empty or bool(value)) and all(text(v) for v in value)



class ReviewContext:
    """Caller-owned frozen packet. The response cannot choose its own threshold.

    Normalize already supplied context into confidence_threshold and sources
    (binding + text records); retain other Run context in the same packet. Source
    identity/admission and filesystem freshness remain caller responsibilities.
    """

    def __init__(self, packet: dict[str, Any]):
        snapshot = deepcopy(packet)
        if not probability(snapshot.get("confidence_threshold")):
            raise ValueError("invalid caller confidence threshold")
        self.confidence_threshold = snapshot["confidence_threshold"]
        self._configure_contract(snapshot)
        self.relation_ordering = validate_ordering_policy(snapshot.get('relation_ordering'))
        self.preflight = snapshot.get('preflight', {})
        self.authority_bindings = snapshot.get('authority_bindings')
        if self.authority_bindings is not None and not isinstance(self.authority_bindings, list):
            raise ValueError('authority_bindings must be an explicit binding list')
        raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode()
        self.sha256 = hashlib.sha256(raw).hexdigest()
        self._sources: dict[str, dict[str, Any]] = {}
        sources = snapshot.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError("context requires bound source texts")
        for record in sources:
            if not isinstance(record, dict) or not isinstance(record.get("binding"), dict):
                raise ValueError("invalid context source")
            binding = record["binding"]
            if not {"atom_id", "version", "path", "sha256"} <= binding.keys():
                raise ValueError("incomplete context source binding")
            if not text(binding["path"]) or not text(record.get("text")):
                raise ValueError("missing source path or text")
            if hashlib.sha256(record["text"].encode()).hexdigest() != binding["sha256"]:
                raise ValueError("source text contradicts binding")
            if binding["path"] in self._sources:
                raise ValueError("duplicate context source path")
            self._sources[binding["path"]] = record
        validate_baseline_sources(snapshot)
        self._principles = {row['binding']['path']: row
                            for row in validated_principle_admissions(snapshot)}
        self._candidates = validated_candidate_bindings(snapshot)
    def _configure_contract(self, snapshot):
        constraints = snapshot.get('review_constraints', {})
        if not isinstance(constraints, dict):
            raise ValueError('caller review_constraints must be a mapping')
        self.report_contract = constraints.get('report_contract', 4)
        if self.report_contract == 7 and ('operator_precheck' in constraints or 'operator_registry' in constraints):
            raise ValueError('contract 7 excludes the retired operator precheck')
        if type(self.report_contract) is not int or self.report_contract not in (4, 5, 6, 7):
            raise ValueError('caller report_contract must be 4, 5, 6 or 7')
        if self.report_contract in (6, 7):
            if constraints.get('review_profile') != 'atom_local':
                raise ValueError('local contracts need an explicit atom_local profile')
            if (not isinstance(snapshot.get('candidate_bindings'), list)
                    or len(snapshot['candidate_bindings']) != 1):
                raise ValueError('atom_local context needs exactly one candidate')
            if not isinstance(snapshot.get('authority_bindings'), list):
                raise ValueError('atom_local context needs an explicit rule allowlist')
            if snapshot['candidate_bindings'][0] in snapshot['authority_bindings']:
                raise ValueError('a local candidate cannot admit itself as a checking rule')

    def source_text(self, binding: Any) -> str:
        if not isinstance(binding, dict) or not text(binding.get("path")):
            raise ValueError("invalid source binding")
        record = self._sources.get(binding["path"])
        if record is None or binding != record["binding"]:
            raise ValueError("unbound or changed source")
        return str(record["text"])

    def candidate_text(self, binding: Any) -> str:
        raw = self.source_text(binding)
        if self._candidates is not None and binding not in self._candidates:
            raise ValueError('source is not a selected evaluation candidate')
        return raw

    def authorities(self, bindings: list[Any], *, candidate: Any = None) -> dict[str, str]:
        result = {}
        for binding in bindings:
            if self.authority_bindings is not None and binding not in self.authority_bindings:
                raise ValueError('source is bound as input, not admitted as authority')
            body = self.source_text(binding)
            principle = self._principles.get(binding['path'])
            carried_identity = text(binding.get('atom_id')) and type(binding.get('version')) is int
            if principle is not None:
                if candidate is None:
                    raise ValueError('Principle citation needs a bound candidate')
                self.candidate_text(candidate)
                if candidate['path'] not in principle['applicable_to']:
                    raise ValueError('Principle applicability excludes this candidate')
                if not carried_identity and self.authority_bindings is None:
                    raise ValueError('Legacy Principle citation needs an explicit authority allowlist')
            if principle is None and not carried_identity:
                raise ValueError("authority needs a carried identity")
            ref = authority_reference(binding)
            if ref in result:
                raise ValueError("ambiguous or duplicate authority reference")
            result[ref] = body
        return result

    def authority_paths(self, bindings: list[Any], *, candidate: Any = None) -> dict[str, str]:
        """Return citation addresses only after caller-owned binding admission."""
        self.authorities(bindings, candidate=candidate)
        return {authority_reference(binding): binding['path'] for binding in bindings}

    def authority_targets(self, authorities: dict[str, str]) -> dict[str, str]:
        targets = {}
        for ref, raw in authorities.items():
            props = metadata(raw)
            subjects = props.get('subjects')
            if isinstance(subjects, dict) and text(subjects.get('governs')):
                targets[ref] = subjects['governs']
        return targets

    def admitted_principle_references(self, bindings: list[Any], *, candidate: Any) -> frozenset[str]:
        """Return only context-admitted Principles applicable to this candidate."""
        self.candidate_text(candidate)
        result = set()
        for binding in bindings:
            if not isinstance(binding, dict) or not text(binding.get('path')):
                raise ValueError('invalid authority binding')
            principle = self._principles.get(binding['path'])
            if principle is None:
                continue
            if self.authority_bindings is not None and binding not in self.authority_bindings:
                raise ValueError('source is bound as input, not admitted as authority')
            if candidate['path'] not in principle['applicable_to']:
                raise ValueError('Principle applicability excludes this candidate')
            result.add(authority_reference(binding))
        return frozenset(result)

