"""Create Current native Ticket Assets."""
from datetime import datetime, timezone
import re

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path, native_ticket_asset

from . import common
from .effects import _project_write_lock
from .native_draft import _check_owner, _summary
from .source import bind_query_reader



def _asset_input(selection, params):
    if not isinstance(params, dict) or set(params) != {'newAtom'} or not isinstance(params['newAtom'], dict):
        raise common.InputError('newAtom', 'Supply a Ticket Asset template and Markdown body.')
    values = params['newAtom']
    if (set(values) - {'container'} != {'template', 'body'}
            or not native_ticket_asset(values['template']) or not isinstance(values['body'], str)):
        raise common.InputError('newAtom', 'Supply an admitted Ticket Asset template and Markdown body.')
    container = values.get('container', {'component': 'C00'})
    if container != {'component': 'C00'} and (not isinstance(container, dict) or set(container) != {'atom'}):
        raise common.InputError('container', 'Supply C00 or a Current planning Ticket.')
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or selection.manifest_path.parent not in {selection.root, selection.control_root}):
        raise common.SourceChanged('Selected Project path is invalid.')
    body = values['body']
    summary = _summary(body)
    try:
        body_bytes = body.encode('utf-8')
    except UnicodeError as error:
        raise common.InputError('body', 'Supply a UTF-8 Markdown body.') from error
    return values, container, summary, body_bytes

def create_asset(selection, params, *, current_rows, previous_capture=None):
    values, container, summary, body_bytes = _asset_input(selection, params)
    with _project_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
            if capture.errors:
                raise common.SourceChanged('Native carrier capture is incomplete.')
            owner = _check_owner(selection, container, current_rows, capture)
            pattern = re.compile(re.escape(selection.project_prefix) + r'-T-([0-9]+)')
            numbers = [int(match[1]) for row in capture.atoms if isinstance(row.get('id'), str)
                       and (match := pattern.fullmatch(row['id']))]
            atom_id = f'{selection.project_prefix}-T-{max(numbers, default=0) + 1}'
            header = canonical_native_header({
                'identity': {'atom_id': atom_id},
                'context': {'container': container, 'template': values['template']},
                'state': {'status': 'in_queue', 'version': 1, 'updated_at': datetime.now(timezone.utc).isoformat()},
            })
            try:
                path = native_carrier_path(header, summary, project_root=selection.control_root,
                                           owner_directory=owner[0], owner_template=owner[1])
            except ValueError as error:
                raise common.InputError('summary', 'Asset Header or Summary cannot be projected to a path.') from error
            raw = b'---\n' + yaml.safe_dump(header, sort_keys=False).encode() + b'---\n' + body_bytes
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native Project source is unavailable or changed.') from error
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, path, raw)
        data = {} if outcome.errors else {'artifact': common.saved(selection, path, atom_id, atom_id, 1, 'in_queue')}
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)
