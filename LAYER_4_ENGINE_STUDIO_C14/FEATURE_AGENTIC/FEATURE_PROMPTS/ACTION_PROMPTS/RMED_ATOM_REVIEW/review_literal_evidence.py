"""Validate exact cited and qualified literal evidence spans."""
from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import Any

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.context_builder import metadata
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.review_context import text


def _literal_occurrence_spans(entity: str, source: str) -> list[tuple[int, int]]:
    literal = r'(?<![\w/])' + re.escape(entity) + r'(?![\w/:])'
    return [match.span() for match in re.finditer(literal, source)]



def _section_spans(source: str) -> dict[str, tuple[int, int]]:
    """Return exact Markdown offsets for the section addresses used by reviews."""
    sections: list[tuple[str, int]] = [('body:preamble', 0)]
    fence: str | None = None
    offset = 0
    for number, line in enumerate(source.splitlines(keepends=True), 1):
        stripped = line.rstrip('\r\n')
        match = re.match(r'^\s*(`{3,}|~{3,})', stripped)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None and re.match(r'^#{1,6}\s', stripped):
            sections.append((f'body:{number}:{stripped.strip()}', offset))
        offset += len(line)
    return {address: (start, sections[index + 1][1] if index + 1 < len(sections) else len(source))
            for index, (address, start) in enumerate(sections)}



def _citation_binding(mention, authorities, authority_paths):
    evidence = mention.get('citation_evidence')
    if not isinstance(evidence, dict):
        raise ValueError('invalid citation evidence')
    authority = evidence.get('authority')
    atom_id = evidence.get('atom_id')
    filename = evidence.get('filename')
    spans = evidence.get('spans')
    if (not text(authority) or not text(atom_id) or not text(filename)
            or not isinstance(spans, list) or not spans):
        raise ValueError('citation evidence needs authority, Atom ID, filename, and spans')
    bound = authorities.get(authority)
    if bound is None:
        raise ValueError('citation evidence authority is not bound')
    props = metadata(bound)
    version = props.get('version')
    if props.get('atom_id') != atom_id or type(version) is not int or authority != f'{atom_id}@{version}':
        raise ValueError('citation evidence does not identify its exact bound Atom source')
    path = (authority_paths or {}).get(authority)
    if not text(path) or not path.endswith('.md'):
        raise ValueError('citation evidence needs a bound Markdown Carrier path')
    label = PurePosixPath(path).name[:-3]
    if filename != label:
        raise ValueError('citation filename differs from the complete bound filename without .md')
    matching_paths = {value for ref, value in (authority_paths or {}).items()
                      if ref in authorities and text(value) and value.endswith('.md')
                      and PurePosixPath(value).name[:-3] == label}
    if len(matching_paths) != 1:
        raise ValueError('citation filename is ambiguous across bound sources')
    return spans, label


def _validate_citation_evidence(mention: dict[str, Any], source: str,
                                authorities: dict[str, str],
                                authority_paths: dict[str, str] | None) -> list[tuple[int, int]]:
    """Admit exact filename-without-.md citation spans from bound addresses.

    This deliberately validates provenance and location, not whether a
    reviewer correctly classified a citation as non-substantive.  Such spans
    can exempt only their own characters from the declared-target literal
    guard below. The caller's admitted path supplies the filename; response
    fields, Atom IDs, Summaries and surrounding folders cannot reconstruct it.
    """
    spans, label = _citation_binding(mention, authorities, authority_paths)
    sections = _section_spans(source)
    claimed_sections = [address for address in sections
                        if address == mention['location']
                        or address.split(':', 2)[-1].lstrip('# ') == mention['location']]
    if len(claimed_sections) != 1:
        raise ValueError('citation evidence has no unambiguous claimed Markdown section')
    validated: list[tuple[int, int]] = []
    for span in spans:
        if (not isinstance(span, dict) or not text(span.get('section'))
                or type(span.get('start')) is not int or type(span.get('end')) is not int
                or not text(span.get('text'))):
            raise ValueError('invalid citation span')
        section = span['section']
        start, end = span['start'], span['end']
        if section not in sections or section != claimed_sections[0] or start < 0 or end <= start or end > len(source):
            raise ValueError('citation span has an invalid Markdown section or range')
        section_start, section_end = sections[section]
        if start < section_start or end > section_end:
            raise ValueError('citation span falls outside its claimed Markdown section')
        if source[start:end] != span['text'] or span['text'] != label:
            raise ValueError('citation span is not the exact bound filename without .md')
        if span['text'] not in mention['excerpt']:
            raise ValueError('citation span is unrelated to its general mention excerpt')
        validated.append((start, end))
    if len(validated) != len(set(validated)):
        raise ValueError('duplicate citation span')
    return validated



def _qualified_binding(mention, authorities, candidate_binding):
    evidence = mention['qualified_literal_evidence']
    if not isinstance(evidence, dict) or set(evidence) != {'declared_entity', 'mention_span', 'literal_spans'}:
        raise ValueError('invalid qualified literal evidence')
    if mention.get('resolution') != 'resolved' or mention.get('resolution_basis') != 'meaning':
        raise ValueError('qualified literal evidence needs a resolved meaning mention')
    if mention.get('candidate_definition_evidence') is not None:
        raise ValueError('qualified literal evidence cannot use candidate-definition admission')
    proof = mention.get('declared_subject_evidence')
    if not isinstance(proof, dict) or not text(proof.get('authority')):
        raise ValueError('qualified literal evidence needs declared Subject meaning evidence')
    if not isinstance(candidate_binding, dict) or not text(candidate_binding.get('atom_id')):
        raise ValueError('qualified literal evidence needs the bound candidate identity')
    proof_raw = authorities.get(proof['authority'])
    if not text(proof_raw):
        raise ValueError('qualified literal evidence needs a bound declared Subject authority')
    if metadata(proof_raw).get('atom_id') == candidate_binding['atom_id']:
        raise ValueError('qualified literal evidence cannot use a same-Atom candidate alias')
    declared = evidence.get('declared_entity')
    entity = mention.get('entity')
    if not text(declared) or not text(entity) or '/' not in entity or entity.rsplit('/', 1)[1] != declared:
        raise ValueError('qualified literal evidence needs the resolved Entity terminal as declared entity')
    return evidence, declared


def _qualified_mention_span(mention, source, evidence):
    sections = _section_spans(source)
    claimed_sections = [address for address in sections
                        if address == mention['location']
                        or address.split(':', 2)[-1].lstrip('# ') == mention['location']]
    if len(claimed_sections) != 1:
        raise ValueError('qualified literal evidence has no unambiguous mention section')
    span = evidence.get('mention_span')
    if (not isinstance(span, dict) or set(span) != {'section', 'start', 'end', 'text'}
            or not text(span.get('section')) or type(span.get('start')) is not int
            or type(span.get('end')) is not int or not text(span.get('text'))):
        raise ValueError('invalid qualified literal mention span')
    section = span['section']
    start, end = span['start'], span['end']
    if section != claimed_sections[0] or section not in sections or start < 0 or end <= start or end > len(source):
        raise ValueError('qualified literal mention span has an invalid section or range')
    section_start, section_end = sections[section]
    if start < section_start or end > section_end or source[start:end] != span['text'] or span['text'] != mention['excerpt']:
        raise ValueError('qualified literal mention span is not the exact resolved mention excerpt')
    return section, start, end


def _validate_qualified_literal_evidence(mention: dict[str, Any], source: str,
                                         authorities: dict[str, str],
                                         candidate_binding: dict[str, Any] | None) -> tuple[str, list[tuple[int, int]]] | None:
    """Bind reviewer-classified qualified literals to one resolved mention.

    Offsets are Python string (Unicode-codepoint) offsets into ``source`` after
    frontmatter removal.  This validates exact coverage/provenance only; the
    already-validated resolved meaning mention remains responsible for the
    semantic mapping.
    """
    if 'qualified_literal_evidence' not in mention:
        return None
    evidence, declared = _qualified_binding(mention, authorities, candidate_binding)
    section, start, end = _qualified_mention_span(mention, source, evidence)
    literals = evidence.get('literal_spans')
    if not isinstance(literals, list) or not literals:
        raise ValueError('qualified literal evidence needs literal spans')
    expected = [(left, right) for left, right in _literal_occurrence_spans(declared, source)
                if start <= left and right <= end]
    validated: list[tuple[int, int]] = []
    for literal in literals:
        if (not isinstance(literal, dict) or set(literal) != {'section', 'start', 'end', 'text'}
                or literal.get('section') != section or type(literal.get('start')) is not int
                or type(literal.get('end')) is not int or not text(literal.get('text'))):
            raise ValueError('invalid qualified literal span')
        left, right = literal['start'], literal['end']
        if (left < start or right <= left or right > end or source[left:right] != literal['text']
                or literal['text'] != declared or (left, right) not in expected):
            raise ValueError('qualified literal span is not an exact declared-entity occurrence')
        validated.append((left, right))
    if len(validated) != len(set(validated)) or set(validated) != set(expected):
        raise ValueError('qualified literal evidence must account for every literal in its exact mention span')
    return declared, validated

