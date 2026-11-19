"""Isolated checks for the Anechoic structure, Concern, and effect rules."""

from collections.abc import Mapping
from graphlib import TopologicalSorter
from pathlib import Path as FilePath, PurePosixPath
from tempfile import TemporaryDirectory

from subject_notation import Name, Path, parse_subject_expression


def project_tree(relative_path, project_name):
    path = PurePosixPath(relative_path)
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError('Expected a path relative to the selected Project')
    records, *nested = path.parts
    if records != f'.anechoic_{project_name}':
        return 'REAL'
    return {'_PMETA': 'PMETA', '__TKT': 'TKT'}.get(nested[0], 'SPEC') if nested else 'SPEC'


def validate_component_tree(project, parents):
    if project not in parents or parents[project] is not None:
        raise ValueError('The Project must be the root Component')
    for child, parent in parents.items():
        if child != project and parent not in parents:
            raise ValueError(f'{child}: missing parent Component')
    tuple(TopologicalSorter({child: () if parent is None else (parent,)
                             for child, parent in parents.items()}).static_order())


def validate_manifest(component, owner, tier, manifest_fields, project, parents):
    if component == project:
        if owner != project or tier != -1 or len(manifest_fields) > 20:
            raise ValueError('Invalid Project Manifest owner, tier, or field count')
    elif component not in parents or parents[component] != owner or tier != 0:
        raise ValueError('A Component Manifest belongs to its parent at Tier 0')


def validate_package(directory, component_directory, package_id):
    path = PurePosixPath(directory)
    if path.parent != PurePosixPath(component_directory) or package_id not in path.name.split('_'):
        raise ValueError('A specified Package directory includes its ID directly under its Component')


def validate_package_identities(specs):
    identities = {}
    for package_id, atom_id in specs:
        if identities.setdefault(package_id, atom_id) != atom_id:
            raise ValueError(f'{package_id}: a Package has one PKG Spec identity')


def validate_trace(project_root, project_name, relative_path, reference, known_revisions):
    path = (project_root / relative_path).resolve()
    if (not path.is_relative_to(project_root) or not path.exists()
            or project_tree(path.relative_to(project_root), project_name) != 'REAL'):
        raise ValueError('Trace must point to existing Realization under the Project root')
    if reference not in known_revisions:
        raise ValueError(f'Trace revision {reference} does not resolve')


def validate_concern(concern, edges):
    if not isinstance(concern, Mapping) or concern.keys() != {'path', 'subject', 'relation'}:
        raise ValueError('A Concern needs path, subject, and relation')
    expression = parse_subject_expression(concern['path'], subject_profile='approved').expression
    if not isinstance(expression, Path) or not isinstance(expression.head, Name):
        raise ValueError('Expected a full Concern path')
    target = expression.head.value
    for step in expression.steps:
        relation = {'/': 'contained_by', '//': 'narrower_than'}.get(step.operator)
        if relation is None or not isinstance(step.operand, Name):
            raise ValueError(f'Unsupported Concern path hop {step.operator}')
        source = step.operand.value
        if (source, relation, target) not in edges:
            raise ValueError(f'Concern hop is missing: {source} {relation} {target}')
        target = source
    if (concern['subject'], concern['relation'], target) not in edges:
        raise ValueError('Concern subject and relation must resolve at the end of the path')


def policy_targets(owner, atoms, parents, matches):
    components = {owner}
    ready = [owner]
    while ready:
        next_parent = ready.pop()
        children = {child for child, parent in parents.items() if parent == next_parent}
        new = children - components
        components.update(new)
        ready.extend(new)
    return {atom['id'] for atom in atoms if atom['family'] == 'SPEC'
            and atom['component'] in components and matches(atom)}


def validate_solution_support(solutions, contributions):
    graph = {solution: [] for solution in solutions}
    for contribution, supported in contributions:
        if supported not in graph:
            raise ValueError('A contribution must target a Solution')
        if contribution in graph:
            graph[supported].append(contribution)
    tuple(TopologicalSorter(graph).static_order())


def rejected(check, *args):
    try:
        check(*args)
    except ValueError:
        return
    raise AssertionError(f'{check.__name__} accepted an invalid fixture')


def run_cases():
    assert project_tree('engine/service.py', 'anechoic') == 'REAL'
    assert project_tree('.anechoic_anechoic/model.md', 'anechoic') == 'SPEC'
    assert project_tree('.anechoic_anechoic/_PMETA/release.md', 'anechoic') == 'PMETA'
    assert project_tree('.anechoic_anechoic/__TKT/TASKS/task.md', 'anechoic') == 'TKT'
    assert project_tree('.anechoic_anechoic/__TKT/ISSUES/issue.md', 'anechoic') == 'TKT'
    assert project_tree('.anechoic_anechoic/__TKT/ASSETS/report.md', 'anechoic') == 'TKT'
    assert project_tree('.anechoic_billing/model.md', 'billing') == 'SPEC'
    rejected(project_tree, '../other/.anechoic_other/model.md', 'anechoic')

    parents = {'Anechoic': None, 'Meta-ontology': 'Anechoic',
               'Meta-methodology': 'Anechoic', 'Engine Studio': 'Anechoic',
               'Backend Deck': 'Engine Studio', 'MCP Patchbay': 'Engine Studio'}
    validate_component_tree('Anechoic', parents)
    assert {k for k, v in parents.items() if v == 'Anechoic'} == {
        'Meta-ontology', 'Meta-methodology', 'Engine Studio'}
    rejected(validate_component_tree, 'Anechoic', parents | {'Backend Deck': 'Unknown'})
    rejected(validate_component_tree, 'Anechoic', parents | {'Engine Studio': 'Backend Deck'})
    validate_manifest('Anechoic', 'Anechoic', -1, {}, 'Anechoic', parents)
    validate_manifest('Backend Deck', 'Engine Studio', 0, {}, 'Anechoic', parents)
    rejected(validate_manifest, 'Backend Deck', 'Anechoic', 0, {}, 'Anechoic', parents)
    rejected(validate_manifest, 'Anechoic', 'Anechoic', -1, dict.fromkeys(range(21)),
             'Anechoic', parents)
    validate_package('engine/create_order_pkg3344', 'engine', 'pkg3344')
    rejected(validate_package, 'engine/ordinary/create_order_pkg3344', 'engine', 'pkg3344')
    rejected(validate_package, 'engine/create_order_pkg3344', 'engine', 'pkg5555')
    validate_package_identities([('pkg3344', 'AN-S-34'), ('pkg3344', 'AN-S-34')])
    rejected(validate_package_identities, [('pkg3344', 'AN-S-34'), ('pkg3344', 'AN-S-99')])
    with TemporaryDirectory() as directory:
        project = FilePath(directory).resolve()
        (project / 'orders.py').touch()
        (project / '.anechoic_anechoic').mkdir()
        (project / '.anechoic_anechoic/spec.md').touch()
        revisions = {'AN-S-12@1', 'AN-S-12@2'}
        validate_trace(project, 'anechoic', 'orders.py', 'AN-S-12@1', revisions)
        rejected(validate_trace, project, 'anechoic', 'orders.py', 'AN-S-12@3', revisions)
        rejected(validate_trace, project, 'anechoic', '../orders.py', 'AN-S-12@1', revisions)
        rejected(validate_trace, project, 'anechoic', 'missing.py', 'AN-S-12@1', revisions)
        rejected(validate_trace, project, 'anechoic', '.anechoic_anechoic/spec.md',
                 'AN-S-12@1', revisions)

    concern = {'path': 'Model/Graph/Node//Artifact', 'subject': 'atom',
               'relation': 'narrower_than'}
    edges = {('Graph', 'contained_by', 'Model'), ('Node', 'contained_by', 'Graph'),
             ('Artifact', 'narrower_than', 'Node'), ('atom', 'narrower_than', 'Artifact')}
    validate_concern(concern, edges)
    rejected(validate_concern, concern | {'path': 'Model/Node//Artifact'}, edges)
    rejected(validate_concern, concern | {'relation': 'contained_by'}, edges)

    atoms = [dict(id='engine-qa', family='SPEC', component='Backend Deck', lens='QA'),
             dict(id='engine-design', family='SPEC', component='Backend Deck', lens='DES'),
             dict(id='engine-ticket', family='TKT', component='Backend Deck', lens='QA'),
             dict(id='sibling-spec', family='SPEC', component='Meta-ontology', lens='QA')]
    assert policy_targets('Engine Studio', atoms, parents, lambda atom: atom['lens'] == 'QA') == {
        'engine-qa'}
    child_manifest = {'id': 'backend-manifest', 'family': 'SPEC', 'component': 'Engine Studio',
                      'described_component': 'Backend Deck'}
    assert policy_targets('Engine Studio', [child_manifest], parents,
                          lambda atom: atom['component'] == 'Engine Studio') == {'backend-manifest'}
    assert policy_targets('Engine Studio', [child_manifest], parents,
                          lambda atom: atom['component'] == 'Backend Deck') == set()
    validate_solution_support({'A', 'B', 'C'}, [('D', 'A'), ('D', 'B'), ('A', 'B')])
    rejected(validate_solution_support, {'A', 'B'}, [('A', 'B'), ('B', 'A')])
    rejected(validate_solution_support, {'A'}, [('A', 'Not a solution')])


if __name__ == '__main__':
    run_cases()
    print('structure, Concern, and effect review cases passed')
