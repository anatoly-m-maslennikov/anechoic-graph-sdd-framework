"""Collect candidate Source Carriers for one role."""

from __future__ import annotations

import re

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    carrier_status_folder,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.methodology_paths__shared import (
    ROLE_BY_DIRECTORY,
    RELATION_KINDS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    repo_relative,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    Candidate,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    CompileError,
    relations_digest,
    split_frontmatter,
    top_scalar,
    relation_targets,
    derive_atom_id,
    definition_subject,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    sha256_bytes,
)
# fmt: on


def _candidate(
    path,
    relative,
    data,
    frontmatter,
    version_raw,
    places,
    layer,
    order,
    role_root,
    extension_id,
    extension_revision,
):
    defined_term, definition_subject_path, definition_namespace = (
        definition_subject(frontmatter, relative)
    )
    return Candidate(
        layer=layer,
        layer_order=order,
        role=ROLE_BY_DIRECTORY[role_root.name],
        role_directory=role_root.name,
        atom_id=derive_atom_id(path, frontmatter),
        version=int(version_raw),
        source_path=relative,
        source_sha256=sha256_bytes(data),
        basename=path.name,
        priority=top_scalar(frontmatter, "priority"),
        priority_group=top_scalar(
            frontmatter, "applicable_methodology_priority_group"
        ),
        replacements=relation_targets(
            frontmatter, RELATION_KINDS["replacement"]
        ),
        incompatibilities=relation_targets(
            frontmatter, RELATION_KINDS["incompatible"]
        ),
        definition_term=defined_term,
        definition_subject_path=definition_subject_path,
        definition_namespace=definition_namespace,
        output_relative=places.output.as_posix(),
        extension_id=extension_id,
        extension_revision=extension_revision,
        original_relations_sha256=relations_digest(frontmatter),
    )


def _active_version(path, relative, frontmatter, exclude):
    if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
        raise CompileError(
            "source-projection-metadata-present",
            "Authoritative Source Carrier cannot contain projection metadata",
            path=relative,
        )
    status = top_scalar(frontmatter, "status")
    if status not in {"Active", "active"}:
        exclude(
            path,
            "inactive" if status else "status-missing",
            status=status,
        )
        return None
    version_raw = top_scalar(frontmatter, "version")
    if version_raw is None or not re.fullmatch(r"[1-9][0-9]*", version_raw):
        raise CompileError(
            "source-version-invalid",
            "Selected Source Atom revision requires a positive "
            "integer version",
            path=relative,
        )
    return version_raw


def _collect_path(
    path,
    relative,
    places,
    candidates,
    exclude,
    layer,
    order,
    role_root,
    extension_id,
    extension_revision,
):
    data = path.read_bytes()
    frontmatter, _ = split_frontmatter(data, relative)
    version_raw = _active_version(path, relative, frontmatter, exclude)
    if version_raw is None:
        return
    candidates.append(
        _candidate(
            path,
            relative,
            data,
            frontmatter,
            version_raw,
            places,
            layer,
            order,
            role_root,
            extension_id,
            extension_revision,
        )
    )


def _eligible_location(path, role_root, exclude):
    relative_within_role = path.relative_to(role_root)
    if {"archived", "draft", "done", "canceled"}.intersection(
        carrier_status_folder(part) for part in relative_within_role.parts[:-1]
    ):
        exclude(path, "inactive-location")
        return False
    if not path.is_file() or path.is_symlink():
        exclude(path, "not-regular")
        return False
    return True


def _collect_role(
    root,
    places,
    candidates,
    diagnostics,
    exclude,
    layer,
    order,
    role_root,
    extension_id=None,
    extension_revision=None,
):
    if not role_root.exists():
        return
    if not role_root.is_dir() or role_root.is_symlink():
        raise CompileError(
            "source-role-not-directory",
            "Source role Carrier must be a directory",
            path=repo_relative(root, role_root),
        )
    for path in sorted(role_root.rglob("*.md")):
        relative = repo_relative(root, path)
        if not _eligible_location(path, role_root, exclude):
            continue
        try:
            _collect_path(
                path,
                relative,
                places,
                candidates,
                exclude,
                layer,
                order,
                role_root,
                extension_id,
                extension_revision,
            )
        except CompileError as error:
            diagnostics.append({**error.record(), "path": relative})
