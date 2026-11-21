"""Check captured import occurrences against resolved owner boundaries."""

from dataclasses import dataclass
from pathlib import PurePosixPath

from .code_access import allows_import, module_visibility, parse_code_access


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


def check_code_access(ownership, sources, occurrences):  # noqa: C901
    """Return denied and uncertain import sites without capturing source again."""
    problems = []
    rules = {key: parse_code_access(owner['fields'].get('boundaries'))
             for key, owner in ownership.entries.items()}
    for site in occurrences:
        def report(status, reason):
            problems.append(CodeAccessProblem(site.source_path, site.line, site.column,
                                              site.written, status, reason))

        if site.status == 'external':
            continue
        if site.status != 'internal' or site.target_path is None:
            report('uncertain', site.status)
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

        path = PurePosixPath(site.target_path)
        if site.target_kind == 'module':
            path = path.with_suffix('')
            if path.name == '__init__':
                path = path.parent
        parts = path.parts + ((site.unit,) if site.unit else ())
        depth = min(len(path.parts) - 1, len(PurePosixPath(provider['path']).parts))
        names = {'.'.join(parts[index:]) for index in range(depth + 1)}
        imports = []
        ancestor = caller
        while ancestor is not None:
            if ancestor is caller or ancestor['kind'] == 'component':
                imports.append(rules[ancestor['id']][0])
            ancestor = ownership.entries.get(ancestor['parent'])
        exports = rules[provider['id']][1]
        entry = next((name for name in sorted(names, key=len, reverse=True)
                      if exports is not None and name in exports), None)
        if entry is None:
            entry = '.'.join(parts)
        imports = [(closed, selectors | {entry} if selectors.intersection(names) else selectors)
                   if rule is not None else None
                   for rule in imports for closed, selectors in [rule or (False, set())]]
        marker = None
        if site.target_kind == 'module' and path.parent.as_posix() == provider['path']:
            marker = module_visibility(path.name)
        layers = _ordered_layers(ownership, caller, provider)
        if not allows_import(entry, caller, provider, exports, inherited_imports=imports,
                             ordered_layers=layers,
                             marker=marker):
            reason = 'sibling layer order' if layers is not None and layers[1] >= layers[0] else 'code access rule'
            report('denied', reason)
    return tuple(problems)
