"""Pure projection of authored native carrier fields into a Markdown path."""
from collections.abc import Mapping
from pathlib import Path
import re
import unicodedata

from .native_carrier_header__pub import native_header_view


DRAFT_DIRECTORY = '01_draft'
ARCHIVE_DIRECTORY = '09_archived'
READY_DIRECTORY = '02_ready'
COMPLETE_DIRECTORY = '08_complete'
TICKET_DIRECTORY = '__TICKETS'
PROJECT_CONFIG_DIRECTORY = '__PROJECT_CONFIG'
CUSTOM_MODEL_DIRECTORY = 'CUSTOM_MODEL'

_LENS_LAYOUT = '_{lens}/{sublenses}'
_DEFAULT_SPEC_LAYOUT = {'0': '.', '1': '01_TIER_1_ARCHITECTURE', '2+': _LENS_LAYOUT}
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
    return (f'_{parts[0].upper()}', *(part.upper() for part in parts[1:]))


def spec_folder_layout(parameters=None):
    """Read the Tier layout, with defaults for Projects without a declaration."""
    project = (parameters or {}).get('project', {})
    if not isinstance(project, Mapping) or 'folder_layout' not in project:
        return _DEFAULT_SPEC_LAYOUT.copy()
    folders = project['folder_layout']
    layout = folders.get('active_spec_by_tier') if isinstance(folders, Mapping) else None
    tier_one = layout.get('1') if isinstance(layout, Mapping) else None
    if (not isinstance(tier_one, str) or re.fullmatch(r'01_[A-Z][A-Z0-9_]*', tier_one) is None
            or re.search(r'_C[0-9]+$', tier_one) is not None
            or tier_one.casefold() == DRAFT_DIRECTORY or len(tier_one) > 255
            or layout != {**_DEFAULT_SPEC_LAYOUT, '1': tier_one}):
        raise ValueError('Invalid Project Manifest project.folder_layout.active_spec_by_tier')
    return dict(layout)


def component_manifest_parent(source_path, parameters=None):
    """Return the owning directory of a control-relative Component Manifest."""
    parent = source_path.parent
    return parent.parent if parent.name in {'_SPEC', spec_folder_layout(parameters)['1']} else parent


def active_spec_directories(tier, lens_directories, *, parameters=None, atom_owned=False):
    if atom_owned:
        return lens_directories
    if tier == -1:
        return ()
    layout = spec_folder_layout(parameters)
    folder = layout.get(str(tier), layout['2+'])
    if folder == '.':
        return ()
    if folder == _LENS_LAYOUT:
        return lens_directories
    return (folder,)


def project_goal_filename(name):
    return re.fullmatch(r'[A-Z]+-S-[0-9]+-SPEC-PROJECT_GOAL--.+\.md', name) is not None


def native_carrier_path(header, summary, *, project_root, owner_directory, owner_template=None, parameters=None):
    """Project a path from authored Header and Summary, without filesystem access.

    The caller resolves the authored container: owner_directory is the Component
    directory for Component-owned SPEC, or the companion directory of an
    owning Atom. For Atom-owned TKT, owner_template is the owner's authored
    template. project_root is the resolved Project control directory.
    parameters are the selected Project Manifest parameters.
    Unknown templates need further placement rules. The function does not validate paths or
    check collisions; those checks belong to the caller.
    """
    view = native_header_view(header)
    family = view.get('atom_family')
    if family not in {'SPEC', 'PROJECT_CONFIG', 'TKT'}:
        raise ValueError('An authored native Atom Family is required')
    atom_id = view['identity']['atom_id']
    context, state = view['context'], view['state']
    status, version = state['status'].lower(), state['version']
    model_ticket_status = family == 'TKT' and re.fullmatch(r'[a-z][a-z0-9_]*', status) is not None
    if (not model_ticket_status
            and status not in {'active', 'in_queue', 'backlog', 'done', 'complete', 'canceled', 'resolved', 'draft', 'ready', 'archived'}
            or (status == 'ready' and family != 'SPEC') or (status in {'in_queue', 'complete'} and family != 'TKT')):
        raise ValueError('Unsupported authored Status')
    revision = DRAFT_DIRECTORY if status == 'draft' else ARCHIVE_DIRECTORY if status == 'archived' else None
    marker = atom_id + (f'@{version}-draft' if status == 'draft' else f'@{version}' if status == 'archived' else '')
    root = Path(project_root)
    atom_owned = 'atom' in context['container']
    if atom_owned and owner_directory is None:
        raise ValueError('Resolved Atom companion directory is required')
    if family == 'SPEC':
        root, stem = _spec_placement(header, context, status, revision, marker, project_root,
                                     owner_directory, atom_owned, parameters)
    else:
        root, stem = _other_placement(family, context, status, revision, marker, root, owner_directory, owner_template, atom_owned)
    return root / (stem + '--' + _slug(summary) + '.md')


def _spec_placement(header, context, status, revision, marker, project_root, owner_directory, atom_owned, parameters):
    if owner_directory is None:
        raise ValueError('Resolved Component directory is required')
    tier = header.get('tier', context.get('tier'))
    root = Path(project_root if tier == -1 and not atom_owned else owner_directory)
    if (status == 'active' and tier == -1 and context.get('container') == {'component': 'C00'}
            and context.get('template') in {'project_manifest', 'project_goal'}):
        root = root.parent
    lens = context.get('lens')
    lens_directories = spec_lens_directories(lens)
    stem = marker + '-' + lens.rsplit('/', 1)[-1].upper()
    if context.get('template'):
        stem += '-' + _token(context['template'])
    if revision:
        root /= revision
    elif status == 'ready':
        root /= READY_DIRECTORY
    else:
        root = root.joinpath(*active_spec_directories(tier, lens_directories,
                                                      parameters=parameters, atom_owned=atom_owned))
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
    if family == 'PROJECT_CONFIG':
        root = Path(owner_directory) if atom_owned else root / PROJECT_CONFIG_DIRECTORY
        if template == 'model_manifest':
            if context['container'] != {'component': 'C00'}:
                raise ValueError('Model Manifest requires the Project Component')
            root /= CUSTOM_MODEL_DIRECTORY
    if family == 'PROJECT_CONFIG' and status == 'draft' and not template:
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
