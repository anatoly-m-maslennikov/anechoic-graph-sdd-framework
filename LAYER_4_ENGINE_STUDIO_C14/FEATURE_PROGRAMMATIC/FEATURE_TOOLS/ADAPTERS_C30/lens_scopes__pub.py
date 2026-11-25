"""Expand and compare the Lens scopes declared by a Project."""

from graphlib import CycleError, TopologicalSorter
from itertools import combinations

from .native_carrier_placement__pub import spec_lens_directories


def compile_lens_groups(parameters):
    project = (parameters or {}).get('project')
    if not isinstance(project, dict) or 'lens_groups' not in project:
        return {}
    definitions = project['lens_groups']
    if not isinstance(definitions, dict):
        raise ValueError('Project Manifest lens_groups must be a mapping')
    for name, members in definitions.items():
        if (len(spec_lens_directories(name)) != 1 or not isinstance(members, list)
                or not members):
            raise ValueError(f'Lens group {name!r} must have a simple name and a nonempty list of members')
        for member in members:
            spec_lens_directories(member)

    dependencies = {name: [member for member in members if member in definitions]
                    for name, members in definitions.items()}
    try:
        order = tuple(TopologicalSorter(dependencies).static_order())
    except CycleError as error:
        raise ValueError(f"Lens group cycle: {' -> '.join(error.args[1])}") from error
    groups = {}
    for name in order:
        groups[name] = frozenset(path for member in definitions[name]
                                 for path in groups.get(member, (member,)))
    return groups


def _covers(scopes, path):
    return any(path == scope or path.startswith(scope + '/') for scope in scopes)


def validate_lens_whitelist(lenses, groups):
    scopes = [(name, groups.get(name, (name,))) for name in lenses or ()]
    for (left_name, left), (right_name, right) in combinations(scopes, 2):
        if all(_covers(left, path) for path in right) or all(_covers(right, path) for path in left):
            continue
        if any(_covers(left, path) for path in right) or any(_covers(right, path) for path in left):
            raise ValueError(f'Lens scopes {left_name!r} and {right_name!r} partially overlap')


def lens_is_allowed(lens, lenses, groups):
    return any(_covers(groups.get(name, (name,)), lens) for name in lenses or ())
