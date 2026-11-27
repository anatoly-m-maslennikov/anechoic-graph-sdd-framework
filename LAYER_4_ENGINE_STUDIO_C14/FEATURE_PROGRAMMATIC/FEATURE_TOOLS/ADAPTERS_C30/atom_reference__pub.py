"""Read legacy Atom identifiers and format native exact revision references."""

from pathlib import Path
import re

_NATIVE_REF = re.compile(r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?")
COMPONENT_MANIFEST_FILENAME = re.compile(
    r"[A-Z]+-S-[0-9]+-SPEC-(COMPONENT(?:_SEED)?_MANIFEST)--.+\.md$"
)


def is_native_atom_reference(value) -> bool:
    return isinstance(value, str) and _NATIVE_REF.fullmatch(value) is not None


def atom_identifier(filename: str, explicit: str | None = None) -> str:
    """Resolve stable identity without absorbing mutable \
scope, tier, type, or sequence."""
    if explicit:
        return explicit.strip().strip("\"'")
    name = Path(filename).name
    canonical = re.match(
        r"(?:[0-9]+-)?(CA-[ACDEIMOPR]-[0-9]+)(?:-|\.|@|$)", name
    )
    if canonical:
        return canonical.group(1)
    return name.removesuffix(".md").split("--", 1)[0]


def derive_atom_ref(atom_id: str, version: int, status: str) -> str:
    suffix = "-draft" if status.casefold() == "draft" else ""
    return f"{atom_id}@{version}{suffix}"
