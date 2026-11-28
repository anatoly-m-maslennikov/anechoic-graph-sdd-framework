"""Publish native Drafts with source checks and rollback."""

from hashlib import sha256 as sha256
from pathlib import Path as Path
import re as re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view as native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    spec_lens_directories as spec_lens_directories,
    DRAFT_DIRECTORY as DRAFT_DIRECTORY,
    READY_DIRECTORY as READY_DIRECTORY,
    TICKET_DIRECTORY as TICKET_DIRECTORY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native as revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds as frontmatter_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext as ReadContext,
)

from ... import common as common, effects as effects
from ...effects import _project_write_lock as _project_write_lock
from ..native_draft_guards import (
    _check_owner as _check_owner,
    _native_slug as _native_slug,
    _reject_component_contract as _reject_component_contract,
    _check_first_spec as _check_first_spec,
    is_c9_typed_manifest as is_c9_typed_manifest,
)
from ..sources.native_draft_source__shared import (
    _revision_header as _revision_header,
    _revision_root as _revision_root,
    _state_bytes as _state_bytes,
    _task_path as _task_path,
)
from ..revision.native_draft_revision__shared import _promote_revision as _promote_revision
from .native_draft_promotion_input import (
    _is_custom_replacement as _is_custom_replacement,
    _promotion_input as _promotion_input,
)
from .native_draft_promotion_spec import (
    _preflight_first_spec as _preflight_first_spec,
)
from .native_draft_promotion_new import _preflight_new as _preflight_new
from .native_draft_promotion_cleanup import (
    _cleanup_published_draft as _cleanup_published_draft,
    _preflight_cleanup as _preflight_cleanup,
    _check_cleanup_task_paths as _check_cleanup_task_paths,
    _check_cleanup_rows as _check_cleanup_rows,
)
from ...updates.replacement.native_replacement_promotion import (
    _plan_replacements as _plan_replacements,
    _archive_replacements as _archive_replacements,
)
from .native_draft_custom_replacement import (
    _publish_custom_replacement as _publish_custom_replacement,
)
from ..sources.native_project_spec import (
    PROJECT_SPEC_TEMPLATES as PROJECT_SPEC_TEMPLATES,
    project_spec_template as project_spec_template,
)
from ...sources.source__shared import bind_query_reader as bind_query_reader

from .native_draft_promotion_apply import (
    _promote_new as _promote_new,
    _publish_first_spec as _publish_first_spec,
)
from .native_draft_promotion_dispatch import promote_draft as promote_draft
