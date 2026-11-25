
"""Compile finite Content constraints from Current formal declarations."""
from __future__ import annotations

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    SubjectNotationError as _subject_SubjectNotationError,
    ValueLiteral as _subject_ValueLiteral,
    parse_subject_expression as _subject_parse_subject_expression,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import is_current_requirement_declaration
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.content_records__pub import records_by_path, value_excluding_declared_children
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import iter_formal_claims
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import content_key, content_lines, parse_content, source_markdown

def _native_declaration(row):
    """Parse one native Declaration using the shared Claim parser."""
    if not is_current_requirement_declaration(row) or not isinstance(body := source_markdown(row), str):
        return None
    fences = tuple(iter_formal_claims(body))
    if len(fences) != 1:
        return None
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
    declaration = parse_native_model_claim(fences[0])
    if not declaration or declaration['kind'] != 'entity':
        return None
    return declaration


def _native_content(row, declaration, form_bindings):
    args = declaration['arguments']
    base = args.get('base_path', '')
    if args.get('value_format') not in (None, 'str', 'string', 'markdown') or args.get('dependent_property_name_format') not in (None, 'str', 'string'):
        return None
    if args.get('relation_name') != 'IS_PROPERTY_OF' or not isinstance(base, str):
        return None
    if base == 'Atom' and args.get('entity_name') == 'Content':
        return args, None, None, (), False
    try:
        path = _subject_parse_subject_expression(base).expression
    except _subject_SubjectNotationError:
        return None
    if not isinstance(path, _subject_Path) or not isinstance(path.head, _subject_Name):
        return None
    binding = form_bindings.get(path.head.value)
    if path.head.value != 'Atom' and binding is None:
        return None
    roles = frozenset({binding[0]}) if binding else None
    forms = frozenset({binding[1]}) if binding else None
    names = []
    for step in path.steps:
        if step.operator == '/' and isinstance(step.operand, _subject_Qualification):
            relative = step.operand.relative_path
            components = [relative.head.value] + [x.operand.value for x in relative.steps
                if x.operator == '.' and isinstance(x.operand, _subject_Name)]
            assignment = relative.steps[-1] if relative.steps else None
            if (components not in (['Header', 'Context', 'Role'], ['Header', 'Context', 'Form'])
                    or assignment is None or assignment.operator != ':='
                    or not isinstance(assignment.operand, _subject_ValueLiteral)):
                return None
            if components[-1] == 'Role':
                roles = frozenset({assignment.operand.value})
            else:
                forms = frozenset({assignment.operand.value})
        elif step.operator == '.' and isinstance(step.operand, _subject_Name):
            names.append(step.operand.value)
        else:
            return None
    if not names or names[0] != 'Content':
        return None
    return args, roles, forms, tuple(content_key(name) for name in (*names[1:], args['entity_name'])), bool(binding)


def _native_records(row, native):
    args, roles, forms, path, binding = native
    if classes := args.get('applies_to_entity_classes'):
        roles = frozenset(classes) if roles is None else roles & frozenset(classes)
    source = row.get('ref') or row.get('id')
    result = []
    def add(kind, target, cardinality, children=(), selected_roles=roles):
        if type(cardinality) is int:
            low = high = cardinality
        else:
            low, high = cardinality['minimum'], cardinality['maximum']
        if high is None:
            return
        result.append(dict(kind=kind, path=list(target),
                           roles=sorted(selected_roles) if selected_roles is not None else None,
                           forms=sorted(forms) if forms is not None else None,
                           min=low, max=high, children=list(children), source=source))

    if path:
        occurrence, value = args.get('property_occurrence_cardinality'), args.get('value_cardinality')
        if occurrence is not None and value is not None:
            add('heading', path, occurrence)
            add('heading_value', path, value)
        elif value is not None:
            add('value', path, value)
        if (children_count := args.get('dependent_property_cardinality')) is not None:
            names = args.get('allowed_dependent_property_names', ())
            add('children', path, children_count, sorted(content_key(name) for name in names))
    order_roles = args.get('ordered_dependent_property_roles')
    if order_roles:
        roles = frozenset(order_roles) if roles is None else roles & frozenset(order_roles)
    for first, second in (() if binding else args.get('ordered_dependent_property_pairs', ())):
        add('order', path, 0, (content_key(first), content_key(second)), roles)
    return result


def _native_form_records(row, declaration, role_names):
    args = declaration['arguments']
    content = args.get('form_content')
    if not content or args.get('qualification_property_path') != 'Atom.Header.Context.Form':
        return []
    classes = [item for item in declaration['classes'] if item['name'] == args.get('entity_class')]
    if len(classes) != 1 or len(classes[0]['bases']) != 1:
        raise ValueError(f"{row.get('id')}: Form requires one Role base")
    role = role_names.get(classes[0]['bases'][0], classes[0]['bases'][0])
    source = row.get('ref') or row.get('id')
    def record(kind, path, minimum, maximum, children=()):
        return dict(kind=kind, path=list(path), roles=[role], forms=[args['entity_name']],
                    min=minimum, max=maximum, children=list(children), source=source)
    required = content_key(content['required_value'])
    no_children = content_key(content['no_children'])
    return [record('value', (required,), 1, 1), record('children', (no_children,), 0, 0),
            record('order', (), 0, 0, (content_key(content['after']), required))]


def compile_content_constraints(rows):
    rows = list(rows)
    native = [(row, declaration) for row in rows if (declaration := _native_declaration(row)) is not None]
    role_names = {d['arguments']['entity_class']: d['arguments']['entity_name'] for _, d in native
                  if d['arguments'].get('qualification_property_path') == 'Atom.Header.Context.Role'
                  and d['arguments'].get('entity_class')}
    bindings = {}
    for row, declaration in native:
        args = declaration['arguments']
        if not args.get('project_form_content'):
            continue
        classes = [item for item in declaration['classes'] if item['name'] == args.get('entity_class')]
        if len(classes) != 1 or len(classes[0]['bases']) != 1:
            raise ValueError(f"{row.get('id')}: Form requires one Role base")
        role = role_names.get(classes[0]['bases'][0], classes[0]['bases'][0])
        for name in {args['entity_name'], args['entity_class']}:
            value = (role, args['entity_name'])
            if name in bindings and bindings[name] != value:
                raise ValueError(f'{row.get("id")}: ambiguous Form base {name}')
            bindings[name] = value
    records = []
    for row, declaration in native:
        if item := _native_content(row, declaration, bindings):
            records.extend(_native_records(row, item))
        records.extend(_native_form_records(row, declaration, role_names))
    return [record for _, record in sorted({repr(record): record for record in records}.items())]


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ContentConstraints:
    records: tuple[
        tuple[str, tuple[str, ...], tuple[str, ...] | None, tuple[str, ...] | None, int, int, tuple[str, ...], str],
        ...,
    ]

    def validate(self, row):  # noqa: C901
        body = source_markdown(row)
        parsed = parse_content(body, tolerate_duplicate_siblings=True) if isinstance(body, str) else []
        paths = [tuple(item['property_path']) for item in parsed]
        def applies(record):
            roles, forms = record[2:4]
            return ((roles is None or any(matches_named_value(row.get('role'), role) for role in roles))
                    and (forms is None or any(matches_named_value(row.get('form'), form) for form in forms)))

        applicable = [record for record in self.records if applies(record)]
        declared = {path for kind, path, *_ in applicable if kind not in {'children', 'order'}}
        for kind, path, _, _, _, _, children, _ in applicable:
            if kind in {'children', 'order'}:
                declared.update((*path, child) for child in children)
        by_path = records_by_path(parsed)
        lines = content_lines(body) if isinstance(body, str) else None
        ordering = {}
        for kind, path, roles, forms, low, high, children, source in applicable:
            if kind == 'order':
                ordering.setdefault((path, source), []).append(children)
            elif kind == 'children':
                if path not in paths:
                    continue
                actual = [item[-1] for item in paths if item[:-1] == path and item in declared]
                if (children and any(name not in children for name in actual)) or not low <= len(actual) <= high or len(actual) != len(set(actual)):
                    raise ValueError(f'Content {".".join(path)} requires {low}..{high} unique children from {", ".join(children)} ({source})')
            elif kind == 'heading' and not low <= paths.count(path) <= high:
                raise ValueError(f'Content {".".join(path)} requires {low}..{high} occurrences ({source})')
            elif kind in {'value', 'heading_value'}:
                if path not in paths:
                    continue
                declared_children = frozenset(child for child in declared if child[:-1] == path)
                count = sum(bool(value_excluding_declared_children(item, by_path, declared_children, lines)[1])
                            for item in by_path.get(path, ()))
                if not low <= count <= high:
                    raise ValueError(f'Content {".".join(path)} requires {low}..{high} direct Markdown values ({source})')

        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import order_properties
        for (path, source), pairs in ordering.items():
            actual = [item[-1] for item in paths if item[:-1] == path]
            ordered_names = {name for pair in pairs for name in pair}
            relevant = [name for name in actual if name in ordered_names]
            if relevant != order_properties(relevant, pairs):
                raise ValueError(f'Content {".".join(path) or "root"} Properties are out of order ({source})')


def load_content_constraints(records, source_ids):
    if not isinstance(records, list):
        raise ValueError('invalid Content constraints')
    result, seen = [], set()
    for item in records:
        if not isinstance(item, dict) or set(item) != {'kind', 'path', 'roles', 'forms', 'min', 'max', 'children', 'source'}:
            raise ValueError('invalid Content constraint')
        kind, path, roles, forms, low, high, children, source = (item[k] for k in ('kind', 'path', 'roles', 'forms', 'min', 'max', 'children', 'source'))
        def valid_names(value, nullable=False):
            return (value is None and nullable) or (isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value)))
        if (kind not in ('heading', 'value', 'heading_value', 'children', 'order')
                or not valid_names(path) or (not path and kind != 'order') or not valid_names(roles, True) or not valid_names(forms, True)
                or not valid_names(children) or type(low) is not int or type(high) is not int
                or (kind not in ('children', 'order') and bool(children))
                or (kind == 'order' and (len(children) != 2 or low != 0 or high != 0)) or low < 0 or high < low
                or not isinstance(source, str) or source not in source_ids):
            raise ValueError('invalid Content constraint')
        key = (kind, tuple(path), None if roles is None else tuple(roles), None if forms is None else tuple(forms), low, high, tuple(children), source)
        if key in seen:
            raise ValueError('duplicate Content constraint')
        seen.add(key)
        result.append(key)
    return ContentConstraints(tuple(result))
