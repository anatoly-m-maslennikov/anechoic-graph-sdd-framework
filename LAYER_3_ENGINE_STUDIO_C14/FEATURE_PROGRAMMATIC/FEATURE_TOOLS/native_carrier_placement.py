"""Pure projection of authored native carrier fields into a Markdown path."""
from pathlib import Path
import re
import unicodedata

from native_carrier_header import native_header_view


_ASSETS = {'analysis_report', 'work_report', 'work_log', 'spec_proposal'}
_TKT_BRANCH = {
    'task': 'TASKS', 'epic': 'TASKS',
    'problem': 'ISSUES', 'question': 'ISSUES', 'code_spec_mismatch': 'ISSUES',
    'opportunity': 'ISSUES',
}


def _token(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*', value):
        raise ValueError('Unsupported authored filename token')
    return re.sub(r'[ _-]+', '_', value).upper()


def _slug(summary):
    if not isinstance(summary, str) or not summary.isprintable():
        raise ValueError('Unsupported Summary serialization')
    # Non-ASCII letters need an authored transliteration; punctuation is a separator.
    if any(not c.isascii() and not unicodedata.category(c).startswith('P') for c in summary):
        raise ValueError('Summary requires an ASCII transliteration')
    slug = re.sub(r'[^A-Za-z0-9]+', '-', summary).strip('-').lower()
    if not slug:
        raise ValueError('Summary has no usable slug')
    return slug


def native_ticket_label(template, owner_template):
    if template == owner_template == 'task':
        return 'Subtask'
    if template == owner_template == 'epic':
        return 'Sub-epic'
    return None


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
    if status not in {'active', 'backlog', 'done', 'canceled', 'resolved', 'draft', 'archived'}:
        raise ValueError('Unsupported authored Status')
    revision = '000_draft' if status == 'draft' else '099_archived' if status == 'archived' else None
    marker = atom_id + (f'@{version}-draft' if status == 'draft' else f'@{version}' if status == 'archived' else '')
    root = Path(project_root)
    template = context.get('template')
    atom_owned = 'atom' in context['container']
    if atom_owned and owner_directory is None:
        raise ValueError('Resolved Atom companion directory is required')
    if family == 'SPEC':
        if owner_directory is None:
            raise ValueError('Resolved Component directory is required')
        root = Path(owner_directory)
        lens = context.get('lens')
        lens_directories = spec_lens_directories(lens)
        stem = marker + '-' + lens.rsplit('/', 1)[-1].upper()
        if template:
            stem += '-' + _token(template)
        if revision:
            root /= revision
        else:
            root = root.joinpath(*lens_directories)
    else:
        if family == 'PMETA' and atom_owned:
            root = Path(owner_directory)
        if family == 'PMETA' and status == 'draft' and not template:
            return root / ('' if atom_owned else '_PMETA') / '000_draft' / (marker + '--' + _slug(summary) + '.md')
        if not template:
            raise ValueError('Authored Template is required')
        key = _token(template).lower()
        label = context.get('label') if family == 'TKT' else None
        stem = marker + '-' + _token(label or template)
        if family == 'PMETA':
            if not atom_owned:
                root /= '_PMETA'
        else:
            branch = 'ASSETS' if key in _ASSETS else _TKT_BRANCH.get(key)
            if branch is None:
                raise ValueError('Unsupported TKT Template')
            if owner_template == 'epic' and key not in {'task', 'epic', 'work_report'}:
                raise ValueError('An Epic can contain only Tasks, Epics and Work Reports')
            if atom_owned and owner_template is None:
                raise ValueError('Resolve the authored Atom owner before deriving its path')
            if atom_owned and key in _ASSETS and not (owner_template == 'task' or
                    (key == 'work_report' and owner_template == 'epic')):
                raise ValueError('An Asset can only be bound to a Task, or a Work Report to an Epic')
            if atom_owned:
                root = Path(owner_directory)
                if owner_template == 'epic' and key == 'work_report':
                    root /= 'ASSETS'
            else:
                root = root / '__TKT' / branch
            if not revision and status != 'active':
                root /= status
        if revision:
            root /= revision
    return root / (stem + '--' + _slug(summary) + '.md')
