"""Check captured import occurrences against resolved owner boundaries."""

from dataclasses import dataclass
from pathlib import PurePosixPath

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import module_visibility, parse_code_access

from .code_access import allows_import


@dataclass(frozen=True)
class CodeAccessProblem:
    path: str
    line: int
    column: int
    written: str
    status: str
    reason: str


def _component_lineage(ownership, owner):
    lineage = []
    while owner is not None:
        if owner['kind'] == 'component':
            lineage.append(owner)
        owner = ownership.entries.get(owner['parent'])
    return reversed(lineage)


def _ordered_layers(ownership, caller, provider):
    for source, target in zip(_component_lineage(ownership, caller),
                              _component_lineage(ownership, provider)):
        if source['id'] != target['id']:
            layers = source['fields'].get('layer'), target['fields'].get('layer')
            return layers if all(type(layer) is int for layer in layers) else None
    return None


def _access_decision(site, caller, provider, ownership, rules):
    path = PurePosixPath(site.target_path)
    if site.target_kind == 'module':
        path = path.with_suffix('')
        if path.name == '__init__':
            path = path.parent
    parts = path.parts + ((site.unit,) if site.unit else ())
    depth = min(len(path.parts) - 1, len(PurePosixPath(provider['path']).parts))
    names = {'.'.join(candidate[index:]) for candidate in (path.parts, parts)
             for index in range(depth + 1)}
    imports = []
    ancestor = caller
    while ancestor is not None:
        if ancestor is caller or ancestor['kind'] == 'component':
            imports.append(rules[ancestor['id']])
        ancestor = ownership.entries.get(ancestor['parent'])
    entry = '.'.join(parts)
    provider_component = tuple(_component_lineage(ownership, provider))[-1]
    exact_names = names - {provider['id'], provider_component['id']}
    exact = site.target_kind == 'module' and any(
        rule is not None and not exact_names.isdisjoint(rule[1]) for rule in imports
    )
    imports = [(closed, selectors | {entry} if selectors.intersection(names) else selectors)
               if rule is not None else None
               for rule in imports for closed, selectors in [rule or (False, set())]]
    marker = None
    if site.target_kind == 'module' and path.parent.as_posix() == provider['path']:
        marker = module_visibility(path.name)
    caller_component = tuple(_component_lineage(ownership, caller))[-1]
    if caller_component['id'] == provider_component['id']:
        sibling = (caller['id'] == provider['parent'] or
                   caller['parent'] == provider['parent'])
    else:
        sibling = caller_component['parent'] == provider_component['parent']
    layers = _ordered_layers(ownership, caller, provider)
    if not allows_import(entry, caller, provider, inherited_imports=imports,
                         ordered_layers=layers, marker=marker, sibling=sibling,
                         provider_component=provider_component['id'], exact=exact):
        reason = 'sibling layer order' if layers is not None and layers[1] >= layers[0] else 'code access rule'
        return reason, False
    return None, exact


def _in_test_package(directory):
    return any(part.endswith('__tests') for part in directory.parts)


def check_code_access(ownership, sources, occurrences, *, include_entry_bypasses=False):  # noqa: C901
    """Check captured imports and optionally report direct access outside an entry."""
    problems = []
    rules = {key: parse_code_access(owner['fields'].get('boundaries'))
             for key, owner in ownership.entries.items()}
    for site in occurrences:
        def report(status, reason):
            problems.append(CodeAccessProblem(site.source_path, site.line, site.column,
                                              site.written, status, reason))

        if site.status == 'external':
            continue
        if site.status not in {'internal', 'asset'} or site.target_path is None:
            report('uncertain', site.status)
            continue
        path = PurePosixPath(site.target_path)
        directory = path if site.target_kind == 'package' else path.parent
        if _in_test_package(directory) and not _in_test_package(PurePosixPath(site.source_path).parent):
            report('denied', 'non-test import from Test Package')
            continue
        if site.status == 'asset':
            continue
        caller = ownership.owner(site.source_path)
        provider = ownership.owner(site.target_path, site.target_kind)
        if caller is None or provider is None:
            report('uncertain', 'owner not resolved')
            continue
        if caller['id'] == provider['id']:
            continue
        if site.unit == '*':
            report('uncertain', 'wildcard import')
            continue

        reason, declared = _access_decision(site, caller, provider, ownership, rules)
        if reason is not None:
            report('denied', reason)
        elif include_entry_bypasses and not (
            site.target_kind == 'module' and module_visibility(path.stem) is not None and
            path.parent.as_posix() == provider['path']
        ):
            if declared:
                report('declared_bypass', 'exact import declaration')
            else:
                report('undeclared_bypass', 'Package entry or exact import declaration required')
    return tuple(problems)
