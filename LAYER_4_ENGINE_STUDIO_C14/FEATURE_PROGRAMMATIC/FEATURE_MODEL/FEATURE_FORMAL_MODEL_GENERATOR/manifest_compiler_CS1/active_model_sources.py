"""Select active native Model Claims from the Meta-ontology and Project Config."""
import ast
import os
import re
from dataclasses import replace
from pathlib import Path, PurePosixPath
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _check_relation_references,
    _native_claim,
    _native_claim_text,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    CUSTOM_MODEL_DIRECTORY,
    PROJECT_CONFIG_DIRECTORY,
    ReadContext,
    native_header_view,
    canonical_model_address,
    model_class_target,
    parse_native_model_claim,
    parse_content,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import (
    is_ontology_model_source, ontology_component_path,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from .active_source_claims import (ModelSourceError, _claim_subject, _custom_claims, _source_error,
                                   _typed_manifest, _valid_subject, _validate_model_row)
from .typed_addresses import typed_addresses
from .typed_node_constraints import lower_node_constraints
from .typed_node_lowering import lower_typed_node
from .typed_property_relation_lowering import declared_relation_names, lower_typed_fields, typed_property_subject
def _append_source_claims(source, claims, subjects, records):
    for subject, claim in claims:
        if subject in subjects:
            raise _source_error(source, 'duplicate_model_subject', subject, 'duplicate Model Subject')
        subjects.add(subject)
        records.append((source, subject, claim))
def _collect_active_source(path, is_custom, metadata, body, control, identifiers, subjects, records, typed):
    header = native_header_view(metadata)
    context, state = header.get('context'), header.get('state')
    if not isinstance(context, dict) or not isinstance(state, dict):
        return
    if state.get('status') != 'active':
        return
    if is_custom:
        if (header.get('atom_family') != 'PROJECT_CONFIG' or context.get('template') not in {'model_manifest', 'manifest_node', 'manifest_property', 'manifest_relation'}
                or context.get('container') != {'component': 'C00'}):
            return
    elif (context.get('container') != {'component': 'C9'}
          or not (context.get('lens') == 'SPEC'
                  or (context.get('lens') == 'DES' and context.get('template') == 'manifest_property'))):
        return
    source = str(path.relative_to(control))
    template = context.get('template')
    subject = (_claim_subject(body, source) if not is_custom or template in {'manifest_property', 'manifest_relation'} else None)
    if not is_custom and subject is None:
        if template in {'manifest_node', 'manifest_relation'}:
            raise ValueError(f'{source}: typed Manifest requires a Model Claim scope')
        if template != 'manifest_property':
            return
        if any(section['property_path'] == ['claim_scope'] for section in parse_content(body)):
            raise ValueError(f'{source}: typed Manifest requires a Model Claim scope')
    identity = header.get('identity')
    identifier = identity.get('atom_id') if isinstance(identity, dict) else None
    version = state.get('version')
    if (not isinstance(identifier, str) or not re.fullmatch(r'[A-Z]+-C-[0-9]+' if is_custom else r'[A-Z]+-S-[0-9]+', identifier)
            or (is_custom and not path.name.startswith(identifier + '-'))
            or ('atom_family' not in metadata and not re.fullmatch(re.escape(identifier) + r'-SPEC(?:-[A-Z_]+)?--.+\.md', path.name))
            or type(version) is not int or version < 1):
        raise ValueError(f'{source}: invalid Model source identity, filename or version')
    if identifier in identifiers:
        raise _source_error(source, 'duplicate_model_source', subject, 'duplicate Model source ID')
    identifiers.add(identifier)
    source = f'{source}@{version}'
    _collect_manifest_claims(body, is_custom, source, subject, context, subjects, records, typed)
def _collect_manifest_claims(body, is_custom, source, subject, context, subjects, records, typed):
    sections = parse_content(body)
    typed_section = any(section['property_path'] == ['formal_manifest'] for section in sections)
    if not is_custom and context.get('template') in {'manifest_node', 'manifest_property', 'manifest_relation'} and not typed_section:
        raise ValueError(f'{source}: typed Template requires a Formal Manifest')
    if (is_custom and context.get('template') in {'manifest_node', 'manifest_property', 'manifest_relation'}) or (not is_custom and typed_section):
        if context.get('template') not in {'manifest_node', 'manifest_property', 'manifest_relation'}:
            raise ValueError(f'{source}: typed manifest requires a typed Template')
        _typed_manifest(sections, source, subject, context, typed)
        return
    claims = _custom_claims(body, source) if is_custom else [(subject, _native_claim(body, source, subject))]
    _append_source_claims(source, claims, subjects, records)
def read_active_model_sources(control_root: Path, component_root: Path) -> tuple[tuple[str, str, str], ...]:
    control = Path(os.path.abspath(control_root))
    component = Path(os.path.abspath(component_root))
    try:
        relative = component.relative_to(control).as_posix()
    except ValueError:
        relative = ''
    if ontology_component_path(relative) != PurePosixPath(relative):
        raise ValueError('Meta-ontology Component must be a native C9 descendant of the control root')
    reader = ReadContext([str(control)], dict(CEILINGS))
    records, identifiers, subjects, typed = [], set(), set(), []
    paths = []
    for directory in (component, component / '_SPEC', component / '_DES'):
        if directory.exists() or directory.is_symlink():
            paths.extend((path, False) for path in reader.inventory_shallow(directory))
    for name in dict.fromkeys((PROJECT_CONFIG_DIRECTORY, '__PROJECT_CONFIG', '002_PROJECT_CONFIG')):
        custom = control / name / CUSTOM_MODEL_DIRECTORY
        if custom.exists() or custom.is_symlink():
            paths.extend((path, True) for path in reader.inventory_shallow(custom))
    for path, is_custom in sorted(paths, key=lambda entry: entry[0].as_posix()):
        carrier = parse_carrier(reader.read(path), path)
        _collect_active_source(path, is_custom, carrier.metadata, carrier.body,
                               control, identifiers, subjects, records, typed)
    result = _lower_active_sources(records, subjects, typed, has_c9=component.exists() or component.is_symlink())
    if reader.currentness()['state'] != 'unchanged':
        raise ValueError('Model source inputs changed during selection')
    return result

def compile_active_model_rows(rows, *, has_c9):
    """Lower immutable ingested carrier rows; None selects the reviewed Model."""
    if type(has_c9) is not bool:
        raise ValueError("has_c9 must be a boolean")
    rows = tuple(rows)
    records, identifiers, subjects, typed = [], set(), set(), []
    control = Path("/snapshot")
    seen_paths = set()
    custom_found = False
    for row in rows:
        source = row.get("source_path") if isinstance(row, dict) else None
        exact_ref = row.get("exact_ref") if isinstance(row, dict) else None
        try:
            is_custom = _validate_model_row(row, source, exact_ref, seen_paths)
            custom_found |= is_custom
            _collect_active_source(control / source, is_custom, row["metadata"], row["body"],
                                   control, identifiers, subjects, records, typed)
        except ModelSourceError as error:
            raise ModelSourceError(source, exact_ref, error.detail, code=error.code, subject=error.subject) from error
        except (ValueError, TypeError, KeyError) as error:
            raise ModelSourceError(source, exact_ref, str(error)) from error
    if not has_c9:
        if custom_found:
            raise ValueError("Custom Model sources require an active C9 Model")
        return None
    try:
        return _lower_active_sources(records, subjects, typed, has_c9=True)
    except ModelSourceError as error:
        match = next((row for row in rows if row["source_path"] == error.source_path), None)
        if match:
            raise ModelSourceError(error.source_path, match["exact_ref"], error.detail,
                                   code=error.code, subject=error.subject) from error
        raise
    except (ValueError, SyntaxError) as error:
        message = str(error)
        match = next((row for row in rows if message.startswith(row["source_path"] + "@")), None)
        raise ModelSourceError(match["source_path"] if match else None,
                               match["exact_ref"] if match else None, message) from error



def _check_entity_parent_anchors(records, scoped_nodes):
    """Check each explicit primary entity path against all declared parents."""
    anchors = {}
    entries = []
    for source, subject, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration['arguments']
        if args.get('entity_kind') != 'Primary':
            continue
        target = model_class_target(subject, args.get('entity_name'))
        if target:
            entries.append((source, subject, canonical_model_address(target)))
    for source, subject in scoped_nodes:
        entries.append((source, subject, canonical_model_address(subject)))
    for source, subject, path in entries:
        anchors.setdefault(path, []).append((source, subject))
    aliases = {}
    for path, declarations in anchors.items():
        expression = _subject_parse_subject_expression(path, subject_profile='approved').expression
        terminal = expression.steps[-1].operand if expression.steps else expression.head
        name = getattr(terminal, 'value', None)
        if isinstance(name, str):
            aliases.setdefault(name, []).extend(declarations)
    for source, subject, path in entries:
        expression = _subject_parse_subject_expression(path, subject_profile='approved').expression
        if not expression.steps or expression.steps[-1].operator not in {'/', '//'}:
            continue
        parent = _subject_render_subject(replace(expression, steps=expression.steps[:-1]))
        matches = aliases.get(parent, ()) if not expression.steps[:-1] else anchors.get(parent, ())
        if len(matches) != 1:
            code = 'missing_entity_parent' if not matches else 'ambiguous_entity_parent'
            raise _source_error(source, code, subject, f'{code}: {parent}')

def _classify_typed_sources(typed):
    pending = []
    field_sources = []
    for source, scope, text, kind in typed:
        try:
            tree = ast.parse(text)
        except SyntaxError as error:
            raise ValueError(f"{source}: invalid typed Python: {error.msg}") from error
        classes = [item for item in tree.body if isinstance(item, ast.ClassDef)]
        if len(classes) != 1:
            raise ValueError(f'{source}: typed manifest requires one class')
        bases = {base.id for base in classes[0].bases if isinstance(base, ast.Name)}
        inferred = ('manifest_property' if 'Property' in bases else
                    'manifest_relation' if 'Relation' in bases else 'manifest_constraints' if 'NodeConstraints' in bases else 'manifest_node')
        if kind is not None and kind != inferred and not (kind == 'manifest_node' and inferred == 'manifest_constraints'):
            raise ValueError(f'{source}: typed template and class do not match')
        (field_sources if inferred != 'manifest_node' else pending).append((source, scope, text, inferred))
    return pending, field_sources


def _lower_ready_nodes(pending, records, append_claim, *, require_all):
    while pending:
        progress = False
        for source, scope, text, kind in pending[:]:
            try:
                lowered = lower_typed_node(text, records, scope)
            except ValueError as error:
                if (str(error) in {'unknown typed node base', 'container_type requires a known fixed Model class'}
                        or (not require_all and 'missing or ambiguous inherited Property' in str(error))):
                    continue
                raise _source_error(source, 'invalid_typed_node', scope, str(error)) from error
            for subject, claim in lowered:
                append_claim(source, subject, claim)
            pending.remove((source, scope, text, kind))
            progress = True
        if not progress:
            if require_all:
                source, scope, _, _ = pending[0]
                raise _source_error(source, 'unresolved_typed_node', scope, 'unresolved typed node dependencies')
            break


def _lower_active_sources(records, subjects, typed, *, has_c9):
    pending, field_sources = _classify_typed_sources(typed)
    relation_names = declared_relation_names(records, field_sources)
    addresses, derived_scopes = _resolve_typed_scopes(records, typed, field_sources)
    _check_entity_parent_anchors(records, [(source, scope) for source, scope, _, _ in pending if scope])
    def append_claim(source, subject, claim):
        if subject in subjects:
            raise _source_error(source, 'duplicate_model_subject', subject, 'duplicate Model Subject')
        subjects.add(subject)
        records.append((source, subject, claim))
    _lower_ready_nodes(pending, records, append_claim, require_all=False)
    for source, scope, text, kind in field_sources:
        scope = derived_scopes.get(source, scope)
        if scope is None:
            raise ValueError(f'{source}: typed field requires a Model scope')
        try:
            claim = (lower_node_constraints(text, scope, addresses) if kind == 'manifest_constraints'
                     else lower_typed_fields(kind, text, scope, addresses, relation_names=relation_names))
        except ValueError as error:
            raise ValueError(f'{source}: {error}') from error
        _native_claim_text('```python\n' + claim + '\n```\n', source, scope)
        append_claim(source, scope, claim)
    _lower_ready_nodes(pending, records, append_claim, require_all=True)
    from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import _check_node_classifications
    _check_node_classifications(
        [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records],
        {source for source, _, _, kind in typed if kind in (None, 'manifest_node')},
    )
    if has_c9:
        if not records:
            raise ValueError('No active Model Claims were selected')
        _check_relation_references(records)
    return tuple(records)


def _resolve_typed_scopes(records, typed, field_sources):
    unresolved = {source: text for source, scope, text, kind in field_sources
                  if scope is None and kind == 'manifest_property'
                  and is_ontology_model_source(PurePosixPath(source.rsplit('@', 1)[0]))}
    derived_scopes = {}
    while True:
        addresses = typed_addresses(records, [
            (source, derived_scopes.get(source, scope), text) for source, scope, text, _ in typed
            if source not in unresolved
        ])
        if not unresolved:
            break
        failures = {}
        for source, text in unresolved.items():
            try:
                subject = typed_property_subject(text, addresses)
            except ValueError as error:
                failures[source] = error
            else:
                derived_scopes[source] = _valid_subject(subject, source)
        if len(failures) == len(unresolved):
            source, error = next(iter(failures.items()))
            raise ValueError(f'{source}: {error}') from error
        unresolved = {source: unresolved[source] for source in failures}
    return addresses, derived_scopes
