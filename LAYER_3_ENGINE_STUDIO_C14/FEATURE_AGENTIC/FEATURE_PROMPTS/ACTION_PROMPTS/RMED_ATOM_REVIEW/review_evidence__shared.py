"""Evidence admission, not semantic inference or a replacement for the reviewer."""
from __future__ import annotations

from typing import Any

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.allowed_value_evidence import validate_allowed_value_evidence
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.candidate_definition_evidence import validate_candidate_definition_evidence
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.declared_subject_evidence import validate_declared_subject_evidence
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.context_builder import body_sections, body_section_texts, metadata, prose
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.review_context import ReviewContext as ReviewContext, probability as probability, strings as strings, text as text
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.review_literal_evidence import (
    _literal_occurrence_spans, _validate_citation_evidence, _validate_qualified_literal_evidence,
)


def validate_quotes(quotes: Any, authorities: dict[str, str], *, empty: bool = False) -> None:
    if not isinstance(quotes, list) or (not quotes and not empty):
        raise ValueError("missing bound evidence quotes")
    for quote in quotes:
        if not isinstance(quote, dict) or not text(quote.get("authority")) or not text(quote.get("excerpt")):
            raise ValueError("invalid authority quote")
        if quote["authority"] not in authorities or quote["excerpt"] not in authorities[quote["authority"]]:
            raise ValueError("authority quote is not in the bound source")


def _obligation_states(row: dict[str, Any], authorities: dict[str, str]) -> dict[str, str]:
    records = row.get("obligation_resolutions")
    if not isinstance(records, list):
        raise ValueError("missing obligation resolutions")
    states = {}
    for record in records:
        if not isinstance(record, dict) or not text(record.get("id")) or not text(record.get("reason")):
            raise ValueError("invalid obligation resolution")
        identifier, state = record["id"], record.get("state")
        if identifier in states or state not in ("local", "inherited", "missing", "unresolved", "conflicting"):
            raise ValueError("duplicate or invalid obligation resolution")
        states[identifier] = state
        unresolved = state in ("unresolved", "conflicting")
        local_required = record.get("local_required")
        if type(local_required) is not bool and not (unresolved and local_required is None):
            raise ValueError("obligation must resolve whether local restatement is required")
        validate_quotes(record.get("support"), authorities, empty=unresolved)
        if state == "inherited" and local_required is not False:
            raise ValueError("inherited rule cannot satisfy mandatory local content")
        if unresolved and row["status"] != "blocked":
            raise ValueError("unresolved obligation needs a check-specific gap")
    return states


def validate_obligations(row: dict[str, Any], authorities: dict[str, str]) -> None:
    """Require an explicit inheritance resolution before alleging an omission."""
    states = _obligation_states(row, authorities)
    omissions = set()
    for finding in row["findings"]:
        if finding["kind"] == "omission":
            identifier = finding.get("obligation_id")
            if not text(identifier) or states.get(identifier) != "missing":
                raise ValueError("omission is not supported by resolved missing authority")
            omissions.add(identifier)
    if any(state == "missing" and identifier not in omissions for identifier, state in states.items()):
        raise ValueError("confirmed missing obligation must retain its finding")


def _markdown(source: str) -> str:
    lines = source.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
        if end is None:
            raise ValueError("cannot locate Markdown for Subject evidence")
        source = "".join(lines[end + 1:])
    return source


def _validate_mention(mention: Any, source: str, authorities: dict[str, str],
                      targets: dict[str, str], *, candidate_source: str | None = None,
                      candidate_binding: dict[str, Any] | None = None,
                      admitted_legacy_principles: frozenset[str] = frozenset(),
                      authority_paths: dict[str, str] | None = None) -> bool:
    if not isinstance(mention, dict) or any(not text(mention.get(k)) for k in ("location", "excerpt", "rationale")):
        raise ValueError("invalid Subject mention evidence")
    if mention["excerpt"] not in source:
        raise ValueError("Subject excerpt is not in Markdown")
    _validate_mention_location(mention, source)
    resolution = mention.get("resolution")
    if resolution not in ("resolved", "general", "unresolved"):
        raise ValueError("unknown Subject resolution")
    if mention.get('citation_evidence') is not None and (resolution != 'general' or mention.get('entity') is not None):
        raise ValueError('citation evidence is only allowed on a general non-Entity mention')
    if resolution == "resolved":
        _validate_resolved_mention(mention, authorities, targets, candidate_source=candidate_source,
                                   candidate_binding=candidate_binding,
                                   admitted_legacy_principles=admitted_legacy_principles)
    else:
        if mention.get("entity") is not None:
            raise ValueError("unresolved/general mention cannot assert an Entity path")
        validate_quotes(mention.get("definitions"), authorities, empty=True)
        if mention.get('citation_evidence') is not None:
            _validate_citation_evidence(mention, source, authorities, authority_paths)
    return bool(resolution == "unresolved")


def _validate_resolved_mention(mention: dict[str, Any], authorities: dict[str, str],
                               targets: dict[str, str], *, candidate_source: str | None = None,
                               candidate_binding: dict[str, Any] | None = None,
                               admitted_legacy_principles: frozenset[str] = frozenset()) -> None:
    if not text(mention.get('entity')):
        raise ValueError('resolved Subject needs a full Entity path')
    basis = mention.get('resolution_basis')
    if basis not in ('identity', 'meaning'):
        raise ValueError('resolved Subject needs identity or meaning resolution basis')
    candidate_defined = validate_candidate_definition_evidence(
        mention, candidate_source=candidate_source, candidate_binding=candidate_binding,
        authorities=authorities, targets=targets)
    validate_quotes(mention.get('definitions'), authorities, empty=candidate_defined)
    if basis == 'identity':
        _validate_literal_identity(mention, authorities)
    anchored = False
    for definition in mention['definitions']:
        ref, excerpt = definition['authority'], definition['excerpt']
        if candidate_source is not None and authorities[ref] == candidate_source:
            raise ValueError('evaluation candidate cannot self-admit an exact Entity anchor')
        if excerpt not in prose(authorities[ref]) or len(excerpt.split()) < 4:
            raise ValueError('Entity definition needs substantive body evidence, not a title or metadata')
        anchored = anchored or mention['entity'] == targets.get(ref)
    value_admitted = validate_allowed_value_evidence(
        mention, authorities, targets, candidate_source=candidate_source)
    declared_admitted = validate_declared_subject_evidence(
        mention, authorities, candidate_source=candidate_source,
        admitted_legacy_principles=admitted_legacy_principles)
    if not anchored and not value_admitted and not declared_admitted and not candidate_defined:
        raise ValueError('resolved Subject needs an exact full Entity authority anchor')


def literal_occurs(entity: str, source: str) -> bool:
    return bool(_literal_occurrence_spans(entity, source))


def _validate_literal_identity(mention: dict[str, Any], authorities: dict[str, str]) -> None:
    if not literal_occurs(mention['entity'], mention['excerpt']):
        raise ValueError('identity recognition requires an exact canonical literal, not a paraphrase')
    for citation in mention.get('definitions', []):
        props = metadata(authorities.get(citation.get('authority'), ''))
        if str(props.get('status', '')).casefold() != 'active':
            raise ValueError('literal identity admission needs explicit Active authority')
        if props.get('content_role') not in ('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'):
            raise ValueError('a Concern or Plan is not Entity identity admission authority')


def _validate_mention_location(mention: dict[str, Any], source: str) -> None:
    sections = body_section_texts(source)
    address = mention['location']
    candidates = [value for key, value in sections.items()
                  if key == address or key.split(':', 2)[-1].lstrip('# ') == address]
    if len(candidates) != 1 or mention['excerpt'] not in candidates[0]:
        raise ValueError('Subject excerpt is absent from its claimed Markdown section')


def _validate_sections(inventory: dict[str, Any], source: str) -> None:
    expected_sections = body_sections(source)
    reviewed = inventory.get('sections_reviewed')
    if not isinstance(reviewed, list) or not strings(reviewed, empty=True):
        raise ValueError('invalid reviewed section inventory')
    if len(reviewed) != len(set(reviewed)) or not set(reviewed) <= set(expected_sections):
        raise ValueError('invalid reviewed section inventory')
    if inventory['complete'] and set(reviewed) != set(expected_sections):
        raise ValueError('complete inventory omitted Markdown sections')


def _declared_subjects(source: str) -> list[Any]:
    properties = metadata(source).get('subjects', {})
    declared: list[Any] = []
    if isinstance(properties, dict):
        if text(properties.get('governs')):
            declared.append(properties['governs'])
        if isinstance(properties.get('depends_on'), list):
            declared.extend(properties['depends_on'])
    return declared


def _validate_subject_findings(row: dict[str, Any], resolved: set[str], declared: list[Any]) -> None:
    for finding in row['findings']:
        if finding.get('subject_issue') == 'extra':
            if (finding['kind'] != 'violation' or finding.get('entity') not in declared
                    or finding['entity'] in resolved or not row['subject_inventory']['complete']):
                raise ValueError('extra Subject needs a complete inventory excluding a declared target')
            continue
        if finding.get('entity') not in resolved:
            raise ValueError('Subject finding lacks a resolved Entity mapping')
        if (finding['kind'] == 'violation' and finding.get('entity') not in declared
                and finding.get('subject_issue') != 'governs'):
            raise ValueError('missing Subject requires an omission resolution or explicit governs mismatch')
        if finding['kind'] == 'omission' and finding['entity'] in declared:
            raise ValueError('Subject omission names an already declared Entity')


def _validate_subject_accounting(row: dict[str, Any], resolved: set[str],
                                 declared: list[Any], governs: Any) -> None:
    """Check the reviewer's own set comparison, not the truth of its mappings.

    An incomplete inventory can preserve a target while a contextual reference
    is unresolved. A complete inventory cannot silently drop that uncertainty
    and claim success, or omit a defect implied by its own resolved inventory.
    """
    governing = {f['entity'] for f in row['findings']
                 if f.get('subject_issue') == 'governs'}
    if isinstance(governs, str) and governs in governing:
        raise ValueError('governing mismatch names the Entity already GOVERNS')
    if not row['subject_inventory']['complete']:
        return
    if any(not text(value) for value in declared):
        raise ValueError('complete Subject comparison requires valid declared targets')
    declarations = set(declared)
    omissions = {f['entity'] for f in row['findings'] if f['kind'] == 'omission'}
    extras = {f['entity'] for f in row['findings'] if f.get('subject_issue') == 'extra'}
    if resolved - declarations - omissions - governing:
        raise ValueError('complete Subject inventory has unaccounted resolved targets')
    replaced = {governs} if governing and isinstance(governs, str) else set()
    if declarations - resolved - extras - replaced:
        raise ValueError('complete Subject inventory has unaccounted declared targets')
    duplicates = {value for value in declarations if declared.count(value) > 1}
    violations = {f['entity'] for f in row['findings'] if f['kind'] == 'violation'}
    if duplicates - violations:
        raise ValueError('complete Subject inventory ignores duplicate declared targets')


def _citation_spans(mentions: list[Any], source: str,
                    authorities: dict[str, str],
                    authority_paths: dict[str, str] | None) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for mention in mentions:
        if (isinstance(mention, dict) and mention.get('resolution') == 'general'
                and mention.get('citation_evidence') is not None):
            spans.extend(_validate_citation_evidence(mention, source, authorities, authority_paths))
    return spans


def _uncovered_literal_occurrence(entity: str, source: str,
                                  exempt_spans: list[tuple[int, int]]) -> bool:
    """Keep an extra-target finding guarded by every substantive occurrence."""
    for start, end in _literal_occurrence_spans(entity, source):
        if not any(exempt_start <= start and end <= exempt_end
                   for exempt_start, exempt_end in exempt_spans):
            return True
    return False


def _review_mentions(inventory, mentions, source, candidate_source, authorities, targets,
                     candidate_binding, admitted_legacy_principles, authority_paths):
    unresolved = not inventory["complete"]
    resolved = set()
    qualified_spans: dict[str, list[tuple[int, int]]] = {}
    for mention in mentions:
        ambiguous = _validate_mention(mention, source, authorities, targets,
                                      candidate_source=candidate_source,
                                      candidate_binding=candidate_binding,
                                      admitted_legacy_principles=admitted_legacy_principles,
                                      authority_paths=authority_paths)
        if inventory['complete'] and ambiguous:
            raise ValueError('complete inventory contains unresolved mentions')
        unresolved |= ambiguous
        if mention['resolution'] == 'resolved':
            resolved.add(mention['entity'])
        qualified = _validate_qualified_literal_evidence(
            mention, source, authorities, candidate_binding)
        if qualified is not None:
            declared_entity, spans = qualified
            qualified_spans.setdefault(declared_entity, []).extend(spans)
    return unresolved, resolved, qualified_spans


def validate_subject_inventory(row: dict[str, Any], source: str, authorities: dict[str, str],
                               targets: dict[str, str], *,
                               candidate_binding: dict[str, Any] | None = None,
                               admitted_legacy_principles: frozenset[str] = frozenset(),
                               authority_paths: dict[str, str] | None = None) -> None:
    declared = _declared_subjects(source)
    subjects = metadata(source).get('subjects', {})
    governs = subjects.get('governs') if isinstance(subjects, dict) else None
    inventory = row.get("subject_inventory")
    if not isinstance(inventory, dict) or type(inventory.get("complete")) is not bool:
        raise ValueError("missing structured Subject inventory")
    mentions = inventory.get("mentions")
    if not isinstance(mentions, list):
        raise ValueError("invalid Subject mentions")
    _validate_sections(inventory, source)
    candidate_source = source
    source = _markdown(source)
    unresolved, resolved, qualified_spans = _review_mentions(
        inventory, mentions, source, candidate_source, authorities, targets,
        candidate_binding, admitted_legacy_principles, authority_paths)
    _validate_subject_findings(row, resolved, declared)
    _validate_subject_accounting(row, resolved, declared, governs)
    citation_spans = _citation_spans(mentions, source, authorities, authority_paths)
    for finding in row['findings']:
        if (finding.get('subject_issue') == 'extra'
                and _uncovered_literal_occurrence(
                    finding['entity'], source,
                    citation_spans + qualified_spans.get(finding['entity'], []))):
            raise ValueError('extra Subject has a literal Markdown occurrence requiring resolution')
    if not mentions and row["status"] == "passed":
        raise ValueError("complete Subject review needs positive mention evidence")
    if unresolved and row["status"] != "blocked":
        raise ValueError("unresolved Subject inventory needs a subjects gap")
