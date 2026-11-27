"""Report one Manifest-to-Solution comparison for embedded Contracts."""

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import finding, verdict
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import manifest_shape, outcome_cases


def _direct(directions):
    boundary = directions['manifest_solution']
    contract = directions['contract_solution']
    checked = [contract, boundary] if boundary['facts'] else [contract]
    return {'status': verdict([result['status'] for result in checked]),
            'facts': [*boundary['facts'], *contract['facts']]}


def _record_io_gaps(model, report, action):
    boundaries = model['manifest'].get('boundaries')
    source = model['manifest']['source']
    if any(issue.get('source') == source for issue in report.get('issues', ())):
        return
    direction = report['directions']['manifest_solution']
    facts = direction['facts']
    gaps = []
    if action is None and not any(fact['key'] == 'record' for fact in facts) and manifest_shape(boundaries):
        gaps.append(finding(source, 'boundaries.io.class_shapes',
                            'Class shape obligations were not compared'))
    compared = [(fact.get('action'), fact.get('output'), fact['key'], fact['left'])
                for fact in facts if fact['key'] in ('must_effect', 'forbid_effect')]
    cases, _ = outcome_cases(boundaries)
    for case in cases:
        name, output = case['action'], case['output']
        if action is not None and action != name:
            continue
        required = [(name, output, key, effect) for key in ('must_effect', 'forbid_effect')
                    for effect in case.get(key, ())]
        if any(fact not in compared for fact in required):
            gaps.append(finding(source, f'boundaries.io.server.{name}.outcomes.{output}',
                                'Logical outcome obligations were not compared'))
    if gaps:
        report['unresolved'] = [*report['unresolved'], *gaps]
        direction['status'] = verdict([direction['status'], 'unresolved'])
        direction['facts'] = [*facts, *({'key': gap['field'], 'status': 'unresolved'} for gap in gaps)]
        report['status'] = verdict([report['status'], 'unresolved'])


def report_comparison(model, report, *, action=None):
    _record_io_gaps(model, report, action)
    if not model.get('embedded_contract'):
        return report
    directions = report['directions']
    direct = _direct(directions)
    consistency = [fact for fact in directions['manifest_contract']['facts']
                   if fact['status'] != 'unresolved' or 'right' not in fact or fact['right'] is not None]
    statuses = [direct['status']]
    if consistency:
        status = verdict([fact['status'] for fact in consistency])
        statuses.append(status)
        report['manifest_consistency'] = {'status': status, 'facts': consistency}
    if report['status'] == 'conflicting':
        statuses.append('conflicting')
    if any(report.get(field) for field in ('issues', 'unresolved', 'uncovered_outcomes', 'unmodeled_tool_api')):
        statuses.append('unresolved')
    report['status'] = verdict(statuses)
    report['directions'] = {'manifest_solution': direct}
    report['sources'] = {role: report['sources'][role] for role in ('manifest', 'solution')}
    if 'operations' in report:
        report['operations'] = {
            name: {'manifest_solution': _direct(results)} for name, results in report['operations'].items()
        }
    return report
