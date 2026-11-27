"""Resolve a black-box child call from the caller Solution and the child Manifest."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    derive_atom_ref,
)

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import finding, verdict
from ...LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
    load_manifest,
)
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    normalize_claim,
    validate_manifest,
)
from .._package__shared import compare_delegation

CLI_INPUT_FIELDS = ('arguments', 'input_fields', 'optional_paired_inputs', 'stdin')


def load_manifest_call(root, parent_manifest, parent_solution, child_id, child_pin):
    parent_id = parent_solution['container_component']
    parent = load_boundary_model(root, parent_id, parent_manifest, solution=parent_solution)
    child = load_manifest(root, child_id, child_pin)
    if child_id == parent_id or child['source']['container_component'] != parent_id:
        raise ValueError(f'{child_id} is not a declared child of {parent_id}')
    issues = [*validate_manifest(child)['issues'], *(
        finding(child['source'], 'manifest', message) for message in child.get('contract_issues', ()))]
    workflow, caller_error = normalize_claim('solution', parent['solution'], parent_id)
    if 'contract' in child:
        contract, child_error = normalize_claim('contract', child['contract'], child_id)
    else:
        contract, child_error = None, 'A black-box child call requires a Manifest with an embedded Contract'
    unresolved = [finding(source, field, error) for source, field, error in (
        (parent['solution']['source'], 'solution', caller_error),
        (child['source'], 'manifest', child_error),
    ) if error]
    return parent['solution']['source'], workflow or {}, child, contract or {}, issues, unresolved


def compare_manifest_call(caller, child, required, offered, issues, unresolved, *, lean):
    source = child['source']
    ref = required.get('manifest')
    if not required:
        unresolved.append(finding(caller, 'solution', 'The selected call has no complete child binding'))
    elif not isinstance(ref, str) or not ref.strip():
        required.setdefault('manifest', None)
        unresolved.append(finding(caller, 'solution', 'The selected call needs an exact child Manifest reference'))
    else:
        offered['manifest'] = derive_atom_ref(source['atom_id'], source['version'], source['status'])
    report = compare_delegation({'caller': caller, 'manifest': source},
                                {'caller': required, 'manifest': offered}, manifest_only=True, lean=lean)
    status = verdict([report['status'], 'unresolved']) if unresolved or issues else report['status']
    return {**report, 'status': status, 'issues': issues, 'unresolved': unresolved}
