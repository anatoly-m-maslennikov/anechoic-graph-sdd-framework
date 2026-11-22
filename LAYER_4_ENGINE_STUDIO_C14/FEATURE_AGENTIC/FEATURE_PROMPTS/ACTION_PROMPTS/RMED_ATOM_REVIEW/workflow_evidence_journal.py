"""Persist workflow events and their Project Journal receipts."""
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

WORKFLOW = 'RMED Atoms Base Revise'


def record_event(root, state, event, step, outcome, details, *, save, append_events):
    now = datetime.now(ZoneInfo(state['timezone'])).isoformat()
    value = {'schema_version': 4, 'kind': 'workflow_execution',
        'event_id': str(uuid.uuid4()), 'action_id': state['workflow_run_id'],
        'event': event, 'author': state['author'], 'occurred_at': now,
        'llm_session': state['session'], 'structural_scope': state['scope'],
        'workflow_run_id': state['workflow_run_id'], 'workflow_name': WORKFLOW,
        'step': step, 'outcome': outcome, 'report_path': state['report_path'], 'details': details}
    entry = {'event': value, 'receipt': None}
    state['events'].append(entry)
    state['updated_at'] = now
    save(state)
    try:
        entry['receipt'] = append_events(root, [value],
            author=state['author'], local_date=now[:10], timezone=state['timezone'])[0]
    except (OSError, RuntimeError, ValueError) as error:
        state['recording_blockers'].append({'stage': 'journal',
            'event_id': value['event_id'], 'error': str(error)})
