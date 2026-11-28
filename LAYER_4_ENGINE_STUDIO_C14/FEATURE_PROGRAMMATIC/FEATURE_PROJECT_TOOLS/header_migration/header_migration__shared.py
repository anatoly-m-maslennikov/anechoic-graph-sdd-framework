"""Map old native Headers and paths to current carrier rules."""

from datetime import datetime, timezone
from pathlib import Path
import re


EXCLUDED = {
    "000_ANECHOIC_framework",
    "migration",
    "journal",
    "_migration",
    "_journal",
}
NESTED_CONTROL = ".anechoic_anechoic"


def admitted(path):
    parts = (
        path.parts[1:]
        if path.parts and path.parts[0] == NESTED_CONTROL
        else path.parts
    )
    return not any(p.startswith(".") or p in EXCLUDED for p in parts)


def timestamp_fallback(metadata, path):
    state = metadata.get("state", {})
    original = state.get("updated_at")
    try:
        timestamp = (
            datetime.fromisoformat(original.replace("Z", "+00:00"))
            if isinstance(original, str)
            else original
        )
    except ValueError:
        timestamp = None
    fallback = None
    if not isinstance(timestamp, datetime) or timestamp.utcoffset() is None:
        fallback = datetime.fromtimestamp(
            path.stat().st_mtime, timezone.utc
        ).isoformat()
        state["updated_at"] = fallback
    return original, fallback


def convert_tier(metadata, view, family, was_core, old_ref, recovery, rel):
    if family != "SPEC":
        return None, None
    tier = view["context"].get("tier")
    tier_source = "core" if was_core else None
    if tier is None:
        tier = recovery.get(old_ref, 2)
        tier_source = "recovered" if old_ref in recovery else "defaulted"
    if type(tier) is not int:
        raise ValueError(f"Invalid Tier for {rel}: {tier!r}")
    structure = metadata.get(
        "structure",
        metadata if "atom_family" in metadata else metadata["context"],
    )
    structure["tier"] = tier
    return tier, tier_source


def adjust_status(metadata, view, family, old_status, rel):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.header.header__shared import (native_ticket_asset)  # fmt: skip

    relations = metadata.get("relations", {})
    if "REFERENCES" in relations:
        if "IS_REFERENCE" in relations:
            raise ValueError(f"Conflicting reference relations: {rel}")
        relations["IS_REFERENCE"] = relations.pop("REFERENCES")
    state = view["state"]
    if family == "TKT" and old_status == "active":
        state["status"] = "in_queue"
    if (
        family == "TKT"
        and old_status == "done"
        and "component" in view["context"]["container"]
        and native_ticket_asset(view["context"].get("template"))
    ):
        state["status"] = "complete"


def carrier_destination(
    source, rel, new, view, family, tier, atom_id, old_ref
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.header.header__shared import (
        COMPLETE_DIRECTORY,
        DRAFT_DIRECTORY,
        TICKET_DIRECTORY,
        native_ticket_asset,
    )  # fmt: skip

    suffix = re.sub(
        r"^" + re.escape(atom_id) + r"(?:@\d+(?:-draft)?)?", "", rel.name
    )
    if suffix == rel.name or not suffix.endswith(".md"):
        raise ValueError(f"Unsupported carrier filename: {rel}")
    status = view["state"]["status"].lower()
    marker = old_ref if status in {"draft", "archived"} else atom_id
    new = new.with_name(marker + suffix)
    container = view["context"]["container"]
    if status == "complete" and family == "TKT":
        new = Path(TICKET_DIRECTORY, "ASSETS", COMPLETE_DIRECTORY, new.name)
    elif rel.parts[0] == NESTED_CONTROL:
        if (
            family == "TKT"
            and status == "in_queue"
            and "component" in container
            and native_ticket_asset(view["context"].get("template"))
        ):
            new = Path(TICKET_DIRECTORY, "ASSETS", new.name)
        elif (
            family == "SPEC"
            and status == "draft"
            and rel.parent.name == "000_draft"
        ):
            owner = Path(*rel.parts[1:-2])
            if (
                owner.name.rpartition("_")[2] != container.get("component")
                or not (source / owner).is_dir()
            ):
                raise ValueError(f"Unknown nested SPEC owner: {rel}")
            new = owner / DRAFT_DIRECTORY / new.name
        else:
            raise ValueError(f"Unmapped nested native carrier: {rel}")
    return spec_destination(rel, new, view, family, tier)


def spec_destination(rel, new, view, family, tier):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.header.header__shared import (
        READY_DIRECTORY,
        active_spec_directories,
        spec_lens_directories,
    )  # fmt: skip

    status = view["state"]["status"].lower()
    container = view["context"]["container"]
    if (
        family != "SPEC"
        or "component" not in container
        or status in {"draft", "archived"}
    ):
        return new
    ready = status == "ready"
    if not ready and tier < -1:
        return new
    lens = spec_lens_directories(view["context"]["lens"])
    if not ready and tier == -1:
        if container["component"] != "C00":
            raise ValueError(f"Non-project Tier -1 requires review: {rel}")
        return Path(new.name)
    legacy_lens = (f"_{lens[0]}", *lens[1:])
    owner = new.parent
    if ready and owner.name == READY_DIRECTORY:
        owner = owner.parent
    for folder in (lens, legacy_lens, active_spec_directories(1, lens)):
        if owner.parts[-len(folder) :] == folder:
            owner = owner.parents[len(folder) - 1]
            break
    folders = (
        (READY_DIRECTORY,) if ready else active_spec_directories(tier, lens)
    )
    return owner.joinpath(*folders, new.name)
