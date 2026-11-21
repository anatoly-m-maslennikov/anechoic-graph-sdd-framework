"""Pure projection of authored native carrier fields into a Markdown path."""
from pathlib import Path
import re
import unicodedata

from native_carrier_header import native_header_view


DRAFT_DIRECTORY = '01_draft'
ARCHIVE_DIRECTORY = '09_archived'
READY_DIRECTORY = '02_ready'
COMPLETE_DIRECTORY = '08_complete'
TICKET_DIRECTORY = '001_TICKETS'
PROJECT_CONFIG_DIRECTORY = '002_PROJECT_CONFIG'

_ASSETS = {'analysis_report', 'work_report', 'work_log', 'spec_proposal'}
_TKT_BRANCH = {
    'task': 'TASKS', 'epic': 'TASKS',
    'problem': 'ISSUES', 'question': 'ISSUES', 'code_spec_mismatch': 'ISSUES',
    'opportunity': 'ISSUES',
}


def native_ticket_asset(template):
    return isinstance(template, str) and re.sub(r'[ _-]+', '_', template.lower()) in _ASSETS


def _token(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*', value):
        raise ValueError('Unsupported authored filename token')
    return re.sub(r'[ _-]+', '_', value).upper()


def _slug(summary):
    if not isinstance(summary, str) or not summary.isprintable():
        raise ValueError('Unsupported Summary serialization')
    if any(not c.isascii() and not unicodedata.category(c).startswith('P') for c in summary):
        raise ValueError('Summary requires an ASCII transliteration')
    slug = re.sub(r'[^A-Za-z0-9]+', '-', summary).strip('-').lower()
    if not slug:
        raise ValueError('Summary has no usable slug')
    return slug


def native_ticket_label(template, owner_template, owner_label=None, *, label=None):
    if label is not None:
        _token(label)
        return label
    owner_is_epic = owner_template == 'epic' or (
        isinstance(owner_label, str) and owner_label.casefold() in {'epic', 'sub-epic'}
    )
    if template == 'epic':
        return 'Sub-epic' if owner_is_epic else 'Epic'
    return 'Subtask' if owner_template == 'task' and not owner_is_epic else 'Task'


def spec_lens_directories(lens):
    if not isinstance(lens, str):
        raise ValueError('Authored SPEC Lens is required')
    parts = lens.split('/')
    if any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', part) for part in parts):
        raise ValueError('Invalid SPEC Lens')
    return () if lens.upper() == 'SPEC' else tuple(f'__{part.upper()}' for part in parts)


def native_carrier_path(header, summary, *, project_root, owner_directory, owner_template=None):
    """Project a path from authored Header and Summary, without filesystem access.

    The caller resolves the authored container: owner_directory is the Component
    directory for Component-owned SPEC, or the companion directory of an
    owning Atom. For Atom-owned TKT, owner_template is the owner's authored
    template. project_root is the resolved Project control directory.
    Unknown templates need further placement rules. The function does not validate paths or
    check collisions; those checks belong to the caller.
    """
    view = native_header_view(header)
    family = header.get('atom_family')
    if family not in {'SPEC', 'PMETA', 'TKT'}:
        raise ValueError('An authored native Atom Family is required')
    atom_id = view['identity']['atom_id']
    context, state = view['context'], view['state']
    status, version = state['status'].lower(), state['version']
    if (status not in {'active', 'in_queue', 'backlog', 'done', 'complete', 'canceled', 'resolved', 'draft', 'ready', 'archived'}
            or (status == 'ready' and family != 'SPEC') or (status in {'in_queue', 'complete'} and family != 'TKT')):
        raise ValueError('Unsupported authored Status')
    revision = DRAFT_DIRECTORY if status == 'draft' else ARCHIVE_DIRECTORY if status == 'archived' else None
    marker = atom_id + (f'@{version}-draft' if status == 'draft' else f'@{version}' if status == 'archived' else '')
    root = Path(project_root)
    atom_owned = 'atom' in context['container']
    if atom_owned and owner_directory is None:
        raise ValueError('Resolved Atom companion directory is required')
    if family == 'SPEC':
        root, stem = _spec_placement(header, context, status, revision, marker, project_root, owner_directory, atom_owned)
    else:
        root, stem = _other_placement(family, context, status, revision, marker, root, owner_directory, owner_template, atom_owned)
    return root / (stem + '--' + _slug(summary) + '.md')


def _spec_placement(header, context, status, revision, marker, project_root, owner_directory, atom_owned):
    if owner_directory is None:
        raise ValueError('Resolved Component directory is required')
    tier = header.get('tier', context.get('tier'))
    root = Path(project_root if tier == -1 and not atom_owned else owner_directory)
    lens = context.get('lens')
    lens_directories = spec_lens_directories(lens)
    stem = marker + '-' + lens.rsplit('/', 1)[-1].upper()
    if context.get('template'):
        stem += '-' + _token(context['template'])
    if revision:
        root /= revision
    elif status == 'ready':
        root /= READY_DIRECTORY
    elif atom_owned or tier not in {-1, 0, 1, 2}:
        root = root.joinpath(*lens_directories)
    return root, stem


def _ticket_root(root, key, status, revision, owner_directory, owner_template, atom_owned):
    branch = 'ASSETS' if key in _ASSETS else _TKT_BRANCH.get(key)
    if branch is None:
        raise ValueError('Unsupported TKT Template')
    if atom_owned and owner_template is None:
        raise ValueError('Resolve the authored Atom owner before deriving its path')
    if atom_owned and key in _ASSETS and owner_template not in {'task', 'epic'}:
        raise ValueError('An Asset can only be bound to a planning Ticket')
    if atom_owned:
        root = Path(owner_directory)
        if key in _ASSETS:
            root /= 'ASSETS'
    else:
        root = root / TICKET_DIRECTORY / branch
    if status == 'complete':
        if branch != 'ASSETS' or atom_owned:
            raise ValueError('Only detached Assets use Complete placement')
        root /= COMPLETE_DIRECTORY
    elif not revision and status not in {'active', 'in_queue'}:
        root /= status
    return root


def _other_placement(family, context, status, revision, marker, root, owner_directory, owner_template, atom_owned):
    template = context.get('template')
    if family == 'PMETA':
        root = Path(owner_directory) if atom_owned else root / PROJECT_CONFIG_DIRECTORY
    if family == 'PMETA' and status == 'draft' and not template:
        return root / DRAFT_DIRECTORY, marker
    if not template:
        raise ValueError('Authored Template is required')
    key = _token(template).lower()
    label = context.get('label') if family == 'TKT' else None
    stem = marker + '-' + _token(label or template)
    if family == 'TKT':
        root = _ticket_root(root, key, status, revision, owner_directory, owner_template, atom_owned)
    if revision:
        root /= revision
    return root, stem
