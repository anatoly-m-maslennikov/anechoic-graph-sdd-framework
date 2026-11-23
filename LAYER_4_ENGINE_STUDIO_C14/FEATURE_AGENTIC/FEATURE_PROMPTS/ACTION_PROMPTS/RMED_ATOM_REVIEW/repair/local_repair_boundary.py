"""Preserve graph targets during Atom-local repairs."""
from typing import Any

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import metadata


def _local_repair_boundary(proposal: dict[str, Any], output: dict[str, Any], original: str) -> None:
    """Preserve graph targets while allowing unambiguous Carrier-shape repairs."""
    if proposal['disposition'] in ('replacement', 'split') or output['path'] != proposal['source']['path']:
        raise ValueError('identity-changing or outside-path repairs need a separate authorized run')

    def values(value: Any) -> frozenset[str]:
        if value is None:
            return frozenset()
        if isinstance(value, str) and value:
            return frozenset([value])
        if isinstance(value, list) and all(isinstance(v, str) and v for v in value):
            return frozenset(value)
        raise ValueError('ambiguous graph target encoding cannot be repaired in atom_local')

    def targets(raw: str) -> tuple[Any, Any]:
        props = metadata(raw)
        subjects, relations = props.get('subjects', {}), props.get('relations', {})
        if (not isinstance(subjects, dict) or not isinstance(relations, dict)
                or set(subjects) - {'governs', 'depends_on'}):
            raise ValueError('ambiguous graph target encoding cannot be repaired in atom_local')
        return ((values(subjects.get('governs')), values(subjects.get('depends_on'))),
                {kind: values(refs) for kind, refs in relations.items()})

    if targets(original) != targets(output['text']):
        raise ValueError('atom_local repairs must preserve Subject and relation targets')

