"""Validate the modeled declarations in one parsed Component Manifest."""
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import (
    parse_code_access,
)

from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import finding
from .trace_manifest__pub import outcome_cases


def validate_manifest(manifest):
    """Return source-linked issues and unresolved semantics without reading other artifacts."""
    source = manifest['source']
    fields = manifest['fields']
    if not isinstance(fields, dict):
        return {'issues': [finding(source, 'fields', 'Manifest fields must be a mapping')],
                'unresolved': []}
    issues = _field_issues(fields, source)
    boundaries = fields.get('boundaries')
    if manifest.get('boundaries') != boundaries:
        issues.append(finding(source, 'boundaries', 'Parsed boundaries contradict Manifest fields'))
    if isinstance(boundaries, dict) and isinstance(boundaries.get('state'), dict):
        for name in ('reads', 'writes'):
            value = boundaries['state'].get(name)
            if name in boundaries['state'] and (not isinstance(value, list) or
                                                any(not isinstance(x, str) or not x.strip() for x in value)):
                issues.append(finding(source, f'boundaries.state.{name}', 'Must be a list of nonblank strings'))
    io_complete = False
    try:
        _, io_complete = outcome_cases(boundaries)
    except ValueError as error:
        issues.append(finding(source, 'boundaries.io.server', str(error)))
    imports = None
    try:
        imports = parse_code_access(boundaries)
    except ValueError as error:
        issues.append(finding(source, 'boundaries', str(error)))
    return {'issues': issues, 'unresolved': _unresolved_boundaries(boundaries, imports, source, io_complete)}


def _field_issues(fields, source):
    issues = []
    for name in ('component_id', 'name'):
        if not isinstance(fields.get(name), str) or not fields[name].strip():
            issues.append(finding(source, name, 'Required field must be a nonempty string'))
    unknown = fields.keys() - {'component_id', 'name', 'layer', 'lens_whitelist', 'boundaries'}
    issues.extend(finding(source, name, 'Unknown Manifest field') for name in sorted(unknown))
    if fields.get('layer') is not None and type(fields['layer']) is not int:
        issues.append(finding(source, 'layer', 'Layer must be an integer or null'))
    lenses = fields.get('lens_whitelist')
    if lenses is not None and (not isinstance(lenses, list) or any(not isinstance(x, str) for x in lenses)):
        issues.append(finding(source, 'lens_whitelist', 'Lens whitelist must be a list of strings or null'))
    return issues


def _unresolved_boundaries(boundaries, imports, source, io_complete):
    if boundaries is None or boundaries == {}:
        return [finding(source, 'boundaries', 'No boundary declarations are modeled')]
    if not isinstance(boundaries, dict):
        return []
    unresolved = [finding(source, f'boundaries.{name}', 'Declaration semantics are not modeled')
                  for name in ('process', 'state', 'io')
                  if name in boundaries and not (name == 'state' and boundaries[name] == {'reads': [], 'writes': []})
                  and not (name == 'io' and io_complete)]
    if imports is not None and imports[1]:
        unresolved.append(finding(source, 'boundaries.code.imports', 'Selector resolution requires external context'))
    return unresolved
