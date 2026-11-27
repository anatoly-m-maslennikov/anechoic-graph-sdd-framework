"""Check captured import occurrences against resolved owner boundaries."""

from collections import defaultdict
from pathlib import PurePosixPath

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import module_visibility, parse_code_access

from .code_access import allows_import


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class CodeAccessProblem:
    path: str
    line: int | None
    column: int | None
    written: str
    status: str
    reason: str


def _is_entry(path):
    return path.stem.endswith(("__shared", "__public"))


def _package_entry_problems(sources):
    folders = defaultdict(list)
    parents = {}
    for name in sorted(sources):
        path = PurePosixPath(name)
        if (_in_test_package(path.parent)
                or path.name.endswith((".d.ts", ".d.cts", ".d.mts"))):
            continue
        folders[path.parent].append(path)
        for parent in path.parent.parents:
            if parent.parts:
                parents.setdefault(parent, path)
    problems = []
    for folder in sorted(folders.keys() | parents.keys()):
        files = folders.get(folder, ())
        count = sum(_is_entry(file) for file in files)
        if count != 1:
            anchor = files[0] if files else parents[folder]
            problems.append(CodeAccessProblem(
                anchor.as_posix(), None, None, "Package entry", "denied",
                f"Expected one __shared or __public entry in {folder}, found {count}",
            ))
    return problems


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


def _export_rules(ownership, provider, rules):
    exports = rules[provider['id']][1]
    if exports is not None or provider['kind'] != 'package' or provider['id'] != provider['path']:
        return exports
    component = tuple(_component_lineage(ownership, provider))[-1]
    relative = PurePosixPath(provider['path']).relative_to(component['path'])
    prefix = '.'.join(relative.parts) + '.'
    declared = rules[component['id']][1] or {}
    return {name: rule for name, rule in declared.items() if name.startswith(prefix)} or None


def _access_decision(site, caller, provider, ownership, rules):
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
    exports = _export_rules(ownership, provider, rules)
    entry = next((name for name in sorted(names, key=len, reverse=True)
                  if exports is not None and name in exports), None)
    declared = entry is not None and any(
        rule is not None and not names.isdisjoint(rule[1]) for rule in imports
    )
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
                         ordered_layers=layers, marker=marker):
        reason = 'sibling layer order' if layers is not None and layers[1] >= layers[0] else 'code access rule'
        return reason, False
    return None, declared


def _in_test_package(directory):
    return any(part.endswith('__tests') for part in directory.parts)


def check_code_access(ownership, sources, occurrences, *, include_entry_bypasses=False):  # noqa: C901
    """Check import access and enforce entry rules when requested."""
    problems = _package_entry_problems(sources) if include_entry_bypasses else []
    if ownership is None:
        return tuple(problems)
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
        elif include_entry_bypasses and not (site.target_kind == 'module' and _is_entry(path)):
            if declared:
                report('declared_bypass', 'exact import and export declarations')
            else:
                report('undeclared_bypass', 'Package entry or exact declarations required')
    return tuple(problems)
