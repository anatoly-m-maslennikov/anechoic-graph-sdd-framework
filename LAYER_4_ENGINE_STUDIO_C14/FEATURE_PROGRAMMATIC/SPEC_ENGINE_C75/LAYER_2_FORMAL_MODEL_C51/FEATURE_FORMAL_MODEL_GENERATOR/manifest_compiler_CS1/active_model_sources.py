"""Select active native Model Claims from the Meta-ontology and Project Config."""
import ast
import os
import re
from dataclasses import replace
from pathlib import Path, PurePosixPath
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _check_relation_references,
    _check_node_axes,
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
    NODE_LINK_PREFIX, parse_typed_manifest_node,
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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.continuant_concern__pub import (
    CONTINUANT_LENS, continuant_model_subject, implicit_continuant_node, model_node_location,
    validate_continuant_variant,
)
from .active_source_claims import (ModelSourceError, _claim_subject, _custom_claims, _source_error,
                                   _typed_manifest, _valid_subject, _validate_model_row,
                                   extend_current_status, is_project_model_source)
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
def _collect_active_source(path, is_custom, metadata, body, control, identifiers, subjects, records, typed,
                           node_locations=None):
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
                  or (context.get('lens') == 'DES' and context.get('template') == 'manifest_property')
                  or context.get('lens') == CONTINUANT_LENS)):
        return
    source = str(path.relative_to(control))
    template = context.get('template')
    if (not is_custom and context.get('lens') == CONTINUANT_LENS) or (is_custom and template in {'manifest_node', 'manifest_property', 'manifest_relation'} and header.get('concern') is not None):
        if template not in {'manifest_node', 'manifest_property', 'manifest_relation'}:
            raise ValueError(f'{source}: Continuant Declaration requires a typed Manifest template')
        if any(section['property_path'] == ['claim_scope'] for section in parse_content(body)):
            raise ValueError(f'{source}: Continuant Declaration cannot contain Claim scope')
        subject = continuant_model_subject(header.get('concern'))
        if node_locations is not None and template == 'manifest_node':
            node_locations[subject] = model_node_location(header['concern'])
    else:
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
    _collect_manifest_claims(body, is_custom, source, subject, context, subjects, records, typed, header.get('concern'))
def _collect_manifest_claims(body, is_custom, source, subject, context, subjects, records, typed, concern=None):
    sections = parse_content(body)
    typed_section = any(section['property_path'] == ['formal_manifest'] for section in sections)
    if (not typed_section and not is_custom and context.get('lens') == CONTINUANT_LENS
            and context.get('template') == 'manifest_node'):
        typed.append((source, subject, implicit_continuant_node(concern), 'manifest_node'))
        return
    if not is_custom and context.get('template') in {'manifest_node', 'manifest_property', 'manifest_relation'} and not typed_section:
        raise ValueError(f'{source}: typed Template requires a Formal Manifest')
    if (is_custom and context.get('template') in {'manifest_node', 'manifest_property', 'manifest_relation'}) or (not is_custom and typed_section):
        if context.get('template') not in {'manifest_node', 'manifest_property', 'manifest_relation'}:
            raise ValueError(f'{source}: typed manifest requires a typed Template')
        _typed_manifest(sections, source, subject, context, typed)
        try:
            validate_continuant_variant(concern, context.get('template'), typed[-1][2])
        except ValueError as error:
            raise ValueError(f'{source}: {error}') from error
        return
    claims = _custom_claims(body, source) if is_custom else [(subject, _native_claim(body, source, subject))]
    _append_source_claims(source, claims, subjects, records)
def read_active_model_sources(control_root: Path, component_root: Path, *,
                              node_locations=None, node_metadata=None) -> tuple[tuple[str, str, str], ...]:
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
    if node_locations is None:
        node_locations = {}
    paths = []
    for directory in (component, component / '_SPEC', component / '_DES', component / '_DOM' / 'CONT'):
        if directory.exists() or directory.is_symlink():
            paths.extend((path, False) for path in reader.inventory_shallow(directory))
    for name in dict.fromkeys((PROJECT_CONFIG_DIRECTORY, '__PROJECT_CONFIG', '002_PROJECT_CONFIG')):
        custom = control / name / CUSTOM_MODEL_DIRECTORY
        if custom.exists() or custom.is_symlink():
            paths.extend((path, True) for path in reader.inventory_shallow(custom))
    for path, is_custom in sorted(paths, key=lambda entry: entry[0].as_posix()):
        carrier = parse_carrier(reader.read(path), path)
        _collect_active_source(path, is_custom, carrier.metadata, carrier.body,
                               control, identifiers, subjects, records, typed, node_locations)
    result = _lower_active_sources(records, subjects, typed, has_c9=component.exists() or component.is_symlink(), node_metadata=node_metadata, node_locations=node_locations)
    if reader.currentness()['state'] != 'unchanged':
        raise ValueError('Model source inputs changed during selection')
    return result

def compile_active_model_rows(rows, *, has_c9, node_locations=None, node_metadata=None):
    """Lower immutable ingested carrier rows; None selects the reviewed Model."""
    if type(has_c9) is not bool:
        raise ValueError("has_c9 must be a boolean")
    rows = tuple(rows)
    records, identifiers, subjects, typed = [], set(), set(), []
    if node_locations is None:
        node_locations = {}
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
                                   control, identifiers, subjects, records, typed, node_locations)
        except ModelSourceError as error:
            raise ModelSourceError(source, exact_ref, error.detail, code=error.code, subject=error.subject) from error
        except (ValueError, TypeError, KeyError) as error:
            raise ModelSourceError(source, exact_ref, str(error)) from error
    if not has_c9:
        if custom_found:
            raise ValueError("Custom Model sources require an active C9 Model")
        return None
    try:
        return _lower_active_sources(records, subjects, typed, has_c9=True, node_metadata=node_metadata, node_locations=node_locations)
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
    for index, (source, scope, text, kind) in enumerate(typed):
        try:
            tree = ast.parse(text)
        except SyntaxError as error:
            raise ValueError(f"{source}: invalid typed Python: {error.msg}") from error
        classes = [item for item in tree.body if isinstance(item, ast.ClassDef)]
        if not classes and kind == 'manifest_node':
            node = parse_typed_manifest_node(text)
            bases = ', '.join(node['bases'])
            imports = f'from anechoic.model import {bases}\n' if bases else ''
            signature = f'({bases})' if bases else ''
            text = f"{imports}class {node['name']}{signature}:\n    pass\n"
            typed[index] = (source, scope, text, kind)
            pending.append(typed[index])
            continue
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
                if (str(error) in {'unknown typed node base', 'container_type requires a known fixed Model class', 'unknown ssot_carrier Model class'}
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


def _check_continuant_address(source, scope, text, kind, addresses, claim=None):
    path = PurePosixPath(source.rsplit('@', 1)[0])
    if not is_ontology_model_source(path) or path.parts[-3:-1] != ('_DOM', 'CONT'):
        if kind != 'manifest_node' or path.parts[1:2] != (CUSTOM_MODEL_DIRECTORY,):
            return
    local = scope.split(' <+ ', 1)[1]
    cls = next(item for item in ast.parse(text).body if isinstance(item, ast.ClassDef))
    if kind == 'manifest_node':
        if local.rfind('//') >= 0 and local.rfind('/') == local.rfind('//') + 1:
            parent = local.rsplit('//', 1)[0]
            bases = {addresses.get(base.id) for base in cls.bases if isinstance(base, ast.Name)}
            if parent not in bases:
                raise ValueError(f'{source}: Concern parent is not a direct node base')
    elif kind in {'manifest_property', 'manifest_relation'}:
        args = parse_native_model_claim(claim)['arguments']
        if kind == 'manifest_relation':
            expected = addresses.get('Relation', 'Graph/Relation') + '//' + args['relation_name']
            valid = local == expected
        elif 'entity_name' in args and args.get('entity_kind') == 'Property':
            base = args['base_path']
            suffix = base.partition('.')[2]
            paths = [base] + [path + ('.' + suffix if suffix else '')
                              for path in args.get('applies_to_entity_classes', ())]
            valid = local in {path + '.' + args['entity_name'] for path in paths}
        else:
            return  # Axis scope is checked by its lowering routine.
        if not valid:
            raise ValueError(f'{source}: Concern address does not match Formal Manifest')


def _check_continuant_containment(records, typed):
    pairs = set()
    for _, _, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration['arguments']
        if declaration['kind'] != 'relation' or args.get('relation_name') != 'IS_CONTAINED_BY':
            continue
        for pair in args.get('endpoint_pairs', ()):
            source, target = pair['source_endpoint'], pair['target_endpoint']
            if source.get('level') == target.get('level') == 'model_entities':
                pairs.update((child, parent) for child in source.get('entity_paths', ())
                             for parent in target.get('entity_paths', ()))
    if not pairs:
        return
    for source, scope, text, kind in typed:
        path = PurePosixPath(source.rsplit('@', 1)[0])
        if (kind != 'manifest_node' or not scope or not is_ontology_model_source(path)
                or path.parts[-3:-1] != ('_DOM', 'CONT')):
            continue
        cls = next(item for item in ast.parse(text).body if isinstance(item, ast.ClassDef))
        if any(isinstance(base, ast.Name) and base.id == 'NodeConstraints' for base in cls.bases):
            continue
        local = scope.split(' <+ ', 1)[1]
        if local == 'Model':
            continue
        if local in {'Graph', 'Carrier'}:
            parent = 'Model'
        elif '/' in local and not local[:local.rfind('/')].endswith('/'):
            parent = local.rsplit('/', 1)[0]
        else:
            continue
        if (local, parent) not in pairs:
            raise _source_error(source, 'invalid_continuant_containment', scope,
                                f'Concern containment is absent from IS_CONTAINED_BY endpoint pairs: {parent}')


def _lower_active_sources(records, subjects, typed, *, has_c9, node_metadata=None, node_locations=None):
    pending, field_sources = _classify_typed_sources(typed)
    node_sources = pending[:]
    relation_names = declared_relation_names(records, field_sources)
    addresses, derived_scopes = _resolve_typed_scopes(records, typed, field_sources)
    _check_entity_parent_anchors(records, [(source, scope) for source, scope, _, _ in pending if scope])
    for source, scope, text, kind in pending:
        if scope:
            _check_continuant_address(source, scope, text, kind, addresses)
    def append_claim(source, subject, claim):
        if subject in subjects:
            raise _source_error(source, 'duplicate_model_subject', subject, 'duplicate Model Subject')
        subjects.add(subject)
        records.append((source, subject, claim))
    _lower_ready_nodes(pending, records, append_claim, require_all=False)
    for source, scope, text, kind in sorted(field_sources, key=lambda row: is_project_model_source(row[0])):
        scope = derived_scopes.get(source, scope)
        if scope is None:
            raise ValueError(f'{source}: typed field requires a Model scope')
        try:
            claim = (lower_node_constraints(text, scope, addresses) if kind == 'manifest_constraints'
                     else lower_typed_fields(kind, text, scope, addresses, relation_names=relation_names))
        except ValueError as error:
            raise ValueError(f'{source}: {error}') from error
        _check_continuant_address(source, scope, text, kind, addresses, claim)
        _native_claim_text('```python\n' + claim + '\n```\n', source, scope)
        if (kind == 'manifest_property' and is_project_model_source(source)
                and extend_current_status(source, scope, claim, records, addresses)):
            continue
        append_claim(source, scope, claim)
    _lower_ready_nodes(pending, records, append_claim, require_all=True)
    _collect_node_metadata(records, node_sources, addresses, node_locations, node_metadata)
    _check_continuant_containment(records, typed)
    _check_node_axes(
        [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records],
        {source for source, _, _, kind in typed if kind in (None, 'manifest_node')}
        | {source for source, _, _ in records if is_project_model_source(source)},
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



def _collect_node_metadata(records, typed, addresses, locations, output):
    primary = {}
    for _, subject, claim in records:
        args = parse_native_model_claim(claim)['arguments']
        if args.get('entity_kind') == 'Primary' and args.get('entity_class'):
            primary[model_class_target(subject, args['entity_name'])] = subject
    parts, alternatives, aliases = {}, {}, {}
    sibling_names = {}
    for subject in primary.values():
        if subject in locations:
            parent, _, name = locations[subject]
            sibling_names.setdefault(parent, set()).add(name)
    for source, scope, text, kind in typed:
        if kind != 'manifest_node':
            continue
        node = parse_typed_manifest_node(text)
        if not any(key in node for key in ('parts', 'alternatives', 'aliases')):
            continue
        owner = addresses.get(node['name'])
        subject = primary.get(owner)
        if not subject:
            raise ValueError(f'{source}: node metadata requires an admitted primary node')
        if 'aliases' in node:
            location = locations.get(subject)
            if not location:
                raise ValueError(f'{source}: node aliases require an admitted node location')
            names = sibling_names.setdefault(location[0], set())
            if names.intersection(node['aliases']):
                raise ValueError(f'{source}: node alias collides with a sibling name or alias')
            names.update(node['aliases'])
            aliases[subject] = list(node['aliases'])
        entries, canonical = [], set()
        for label, name in node.get('parts', {}).items():
            path = addresses.get(name)
            target = primary.get(path)
            if not target:
                raise ValueError(f'{source}: unknown or ambiguous node part target: {name}')
            if not label.startswith(NODE_LINK_PREFIX):
                location = locations.get(target)
                if not location or location[1] not in {'/', '//'} or location[0] != owner:
                    raise ValueError(f'{source}: node part is not a direct Concern child: {label}')
                if path in canonical:
                    raise ValueError(f'{source}: node part is already canonical: {label}')
                canonical.add(path)
            entries.append([label, path])
        if entries:
            parts[subject] = entries
        if 'alternatives' in node:
            groups = [list(group) for group in node['alternatives']]
            if any(label not in dict(entries) for group in groups for label in group):
                raise ValueError(f'{source}: node alternative references an undefined part')
            alternatives[subject] = groups
    if output is not None:
        output.update(node_parts=parts, node_alternatives=alternatives, node_aliases=aliases)
