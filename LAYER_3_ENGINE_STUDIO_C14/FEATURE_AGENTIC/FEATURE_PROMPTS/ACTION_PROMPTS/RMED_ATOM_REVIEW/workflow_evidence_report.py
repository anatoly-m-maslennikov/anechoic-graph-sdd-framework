"""Render and encode the complete saved workflow evidence."""
import hashlib
import json
import re

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.workflow_progress import report_progress


def digest(data):
    return hashlib.sha256(data).hexdigest()



def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode()



def block(value):
    text = encoded(value).decode()
    fence = '`' * max(3, max((len(x) + 1 for x in re.findall(r'`+', text)), default=3))
    return f'{fence}json\n{text}\n{fence}\n'



def render_report(state):
    """Full evidence, including pending records; never truncate or invent verdicts."""
    lines = ['# Run\n', block({key: state[key] for key in (
        'workflow_name', 'workflow_run_id', 'definition', 'started_at', 'updated_at',
        'outcome', 'recording_blockers')}), '## Selection\n',
        block({key: state[key] for key in ('request', 'selection', 'gathered', 'exclusions')}),
        '## Rules\n', block(state['criteria']), '## Results\n', block(state['progress']),
        '## Coverage Gates\n', block(state.get('coverage_gates', {})),
        '## Atom Reports\n']
    if not state['selection']:
        lines.append('No Atoms selected.\n' if state['gathered'] else 'Selection pending.\n')
    for i, atom in enumerate(state['selection']):
        lines += [f'### {i + 1}: {atom["atom_id"]}\n', block({
            'source': atom['source'], 'report': state['reports'][i] or {'result': 'pending'},
            'after': state['after'][i], 'history': state['history'][i]})]
    lines += ['## Remaining Work\n', block({
        'pending': [i for i, row in enumerate(state['reports']) if not report_progress(row, check_key=state.get('check_key', 'cce'))['complete']],
        'gather_blockers': state['gather_blockers'], 'handoffs': state['handoffs'],
        'reason': state.get('reason'), 'recording_blockers': state['recording_blockers']}),
        '## Journal\n', block({'path': state['journal'], 'workflow_run_id': state['workflow_run_id'],
            'events': state['events']})]
    return '\n'.join(lines)

