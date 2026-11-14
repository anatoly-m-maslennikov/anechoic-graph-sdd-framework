"""Check a proposed Atom against its pinned revision population."""

from pathlib import Path

from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from .common import InputError, atom_summary
from .source import SourceSelectionError, select_all_revisions


def compile_atom_population_model(rows):
    from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
    from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
    from header_groups import header_value
    from lint_python_model_claim import _canonical_address

    selected = {}
    for row in rows:
        _, subject = header_value(row['header_json'], 'topics.main_subject')
        if not isinstance(subject, str) or not subject.startswith('CAPRMEDIO_MODEL'):
            continue
        address = _canonical_address(subject)
        if address in {'Atom', 'Atom.Content.Summary'}:
            for code in _native_block(row['_content_bytes'].decode('utf-8')):
                if claim := parse_native_model_claim(code):
                    selected[address] = claim['arguments']
    if not selected:
        return False
    atom, summary = selected.get('Atom', {}), selected.get('Atom.Content.Summary', {})
    identity = atom.get('population_unique_constraints')
    summaries = summary.get('population_functional_dependencies')
    if not identity and not summaries:
        return False
    if (identity != ({'keys': ('Header.Identity.ID', 'Header.State.Version')},)
            or summaries != ({'keys': ('Header.Identity.ID',), 'dependents': ('Content.Summary',),
                              'status_groups': ('Current', 'Backlog', 'Archived')},)):
        raise ValueError('Atom population Declarations differ from the supported revision checks')
    return True


def validate_atom_population(selection, *, atom_id, version, status, summary, replaced=(), preserve_summary=False):
    """Return pinned peers after checking identity/version and published Summary.

    The caller revalidates these pins before its effects and excludes only exact
    pinned carriers that its operation replaces or removes.
    """
    if (not isinstance(atom_id, str) or type(version) is not int or version < 1
            or not isinstance(status, str) or not status.strip()
            or not isinstance(summary, str) or not summary.strip()):
        raise ValueError('Invalid proposed Atom population values')
    peers = select_all_revisions(selection, atom_id)
    replaced = tuple(replaced)
    if any(pin not in peers for pin in replaced):
        raise SourceSelectionError('Replaced Atom revision changed during population selection')
    published = status.casefold() != 'draft'
    for peer in peers:
        if peer in replaced:
            continue
        if peer.version == version:
            raise InputError('version', 'Atom ID and Version already exist.')
        if published and not preserve_summary and peer.status.casefold() != 'draft':
            body = parse_carrier(peer.raw, Path(peer.path)).body
            if atom_summary(body).group(1).strip() != summary.strip():
                raise InputError('summary', 'Summary conflicts with another Current, Backlog or Archived revision.')
    return peers


def validate_candidate_population(selection, model, *, atom_id, version, status, summary, replaced=(),
                                  preserve_summary=False):
    if getattr(getattr(model, 'candidate_schema', None), 'atom_population_model', False):
        peers = validate_atom_population(selection, atom_id=atom_id, version=version, status=status,
                                         summary=summary, replaced=replaced, preserve_summary=preserve_summary)
        if select_all_revisions(selection, atom_id) != peers:
            raise SourceSelectionError('Atom revision population changed before publication')
