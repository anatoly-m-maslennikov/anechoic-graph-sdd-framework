#!/usr/bin/env -S python3 -B
"""Build a migrated copy of a staged Project control tree and a receipt.

The source and destination must be outside this checkout. Nothing is written
until every admitted path, Header, and exact reference has passed preflight.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

import yaml

REPO = Path(__file__).resolve().parents[3]
EXCLUDED = {'000_ANECHOIC_framework', 'migration', 'journal', '_migration', '_journal'}
NESTED_CONTROL = '.anechoic_anechoic'
BOUNDARY = re.compile(rb'\A---\r?\n(.*?)\r?\n---\r?\n', re.S)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def admitted(path):
    parts = (
        path.parts[1:]
        if path.parts and path.parts[0] == NESTED_CONTROL
        else path.parts
    )
    return not any(p.startswith(".") or p in EXCLUDED for p in parts)


def reference(atom_id, state):
    status, version = state['status'].lower(), state['version']
    return atom_id + f'@{version}' + ('-draft' if status == 'draft' else '')


def load_codecs():
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        canonical_native_header, native_header_view,
    )
    return native_header_view, canonical_native_header


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
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_ticket_asset

    relations = metadata.get('relations', {})
    if 'REFERENCES' in relations:
        if 'IS_REFERENCE' in relations:
            raise ValueError(f'Conflicting reference relations: {rel}')
        relations['IS_REFERENCE'] = relations.pop('REFERENCES')
    state = view['state']
    if family == 'TKT' and old_status == 'active':
        state['status'] = 'in_queue'
    if (family == 'TKT' and old_status == 'done' and 'component' in view['context']['container']
            and native_ticket_asset(view['context'].get('template'))):
        state['status'] = 'complete'


def carrier_destination(
    source, rel, new, view, family, tier, atom_id, old_ref
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        COMPLETE_DIRECTORY,
        DRAFT_DIRECTORY,
        TICKET_DIRECTORY,
        native_ticket_asset,
    )

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
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        READY_DIRECTORY,
        active_spec_directories,
        spec_lens_directories,
    )

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


def convert_carrier(source, path, rel, new, recovery, refs, header_codecs):
    raw = path.read_bytes()
    match = BOUNDARY.match(raw)
    if not match:
        return None
    metadata = yaml.safe_load(match[1])
    if not isinstance(metadata, dict) or not ('atom_family' in metadata or (
            isinstance(metadata.get('identity'), dict) and 'atom_id' in metadata['identity'])):
        return None
    original, fallback = timestamp_fallback(metadata, path)
    structure = metadata.get('structure', metadata if 'atom_family' in metadata else metadata.get('context', {}))
    was_core = structure.get('tier') == 'core'
    if was_core:
        structure['tier'] = 1
    native_header_view, canonical_native_header = header_codecs
    view = native_header_view(metadata)
    family = view.get('atom_family')
    if family is None:
        family = {'S': 'SPEC', 'T': 'TKT', 'C': 'PROJECT_CONFIG', 'P': 'PROJECT_CONFIG'}[view['identity']['atom_id'].split('-')[-2]]
    elif family == 'PMETA':
        family = 'PROJECT_CONFIG'
    state, atom_id = view['state'], view['identity']['atom_id']
    old_ref, old_status = reference(atom_id, state), state['status']
    if old_ref in refs:
        raise ValueError(
            f"Duplicate reference {old_ref}: {rel}, {refs[old_ref]}"
        )
    refs[old_ref] = str(rel)
    tier, tier_source = convert_tier(
        metadata, view, family, was_core, old_ref, recovery, rel
    )
    adjust_status(metadata, view, family, old_status, rel)
    header = canonical_native_header(metadata)
    new = carrier_destination(
        source, rel, new, view, family, tier, atom_id, old_ref
    )
    newline = b'\r\n' if raw.startswith(b'---\r\n') else b'\n'
    encoded = yaml.safe_dump(header, sort_keys=False, allow_unicode=True).encode().replace(b'\n', newline)
    result = b'---' + newline + encoded + b'---' + newline + raw[match.end():]
    record = {'old_path': str(rel), 'new_path': str(new), 'old_ref': old_ref,
              'new_ref': old_ref, 'old_sha256': digest(raw), 'new_sha256': digest(result),
              'old_status': old_status, 'new_status': state['status'], 'tier_source': tier_source, 'tier': tier,
              'original_updated_at': str(original) if original is not None else None, 'fallback_updated_at': fallback}
    return new, result, record


def preflight(source, entries, recovery, header_codecs):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        ARCHIVE_DIRECTORY, COMPLETE_DIRECTORY, DRAFT_DIRECTORY, PROJECT_CONFIG_DIRECTORY, TICKET_DIRECTORY,
    )

    renames = {'__TKT': TICKET_DIRECTORY, '_PMETA': PROJECT_CONFIG_DIRECTORY,
               '000_draft': DRAFT_DIRECTORY, '099_archived': ARCHIVE_DIRECTORY,
               '999_archive': ARCHIVE_DIRECTORY, '999_archived': ARCHIVE_DIRECTORY,
               '99_archived': ARCHIVE_DIRECTORY}
    paths, carriers, refs, destinations = {}, {}, {}, {}
    for path in entries:
        rel = path.relative_to(source)
        parent = paths.get(rel.parent, rel.parent)
        new = parent / (
            renames.get(rel.name, rel.name) if admitted(rel) else rel.name
        )
        if rel == Path("__TKT/ASSETS/done"):
            new = parent / COMPLETE_DIRECTORY
        if path.is_file() and path.suffix == ".md" and admitted(rel):
            converted = convert_carrier(
                source, path, rel, new, recovery, refs, header_codecs
            )
            if converted:
                new, result, record = converted
                carriers[rel] = result, record
                companion = rel.with_suffix("")
                if (source / companion).is_dir():
                    paths[companion] = new.with_suffix("")
        new = paths.get(rel, new)
        paths[rel] = new
        if new in destinations:
            raise ValueError(
                f"Path collision: {rel} and {destinations[new]} -> {new}"
            )
        destinations[new] = rel
    unknown = set(recovery) - set(refs)
    if unknown:
        raise ValueError(f'Recovery references not found: {sorted(unknown)}')
    check_parents(source, paths, destinations)
    return paths, carriers


def check_parents(source, paths, destinations):
    for target in paths.values():
        for parent in target.parents:
            if (
                parent in destinations
                and (source / destinations[parent]).is_file()
            ):
                raise ValueError(
                    f"File blocks destination directory: {target}"
                )


def write_output(source, destination, entries, paths, carriers):
    destination.mkdir(parents=True)
    try:
        for path in entries:
            rel = path.relative_to(source)
            target = destination / paths[rel]
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                if rel in carriers:
                    target.write_bytes(carriers[rel][0])
                    shutil.copystat(path, target)
                else:
                    shutil.copy2(path, target)
        receipt = {'source': str(source), 'destination': str(destination),
                   'carriers': [record for _, record in carriers.values()]}
        (destination.parent / (destination.name + '.receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    except Exception:
        shutil.rmtree(destination)
        raise
    return receipt


def run(source, destination, recovery):
    source, destination = source.resolve(), destination.resolve()
    if (source == REPO or REPO in source.parents or source == destination or source in destination.parents
            or destination == REPO or REPO in destination.parents):
        raise ValueError('Source must be a staged copy outside the checkout and destination')
    if destination.exists() or (destination.parent / (destination.name + '.receipt.json')).exists() or not source.is_dir():
        raise ValueError('Source must exist and destination must not exist')
    entries = sorted(source.rglob('*'), key=lambda p: (len(p.relative_to(source).parts), p.is_dir(), str(p)))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Symlinks are unsupported in the staged tree')
    header_codecs = load_codecs()
    paths, carriers = preflight(source, entries, recovery, header_codecs)
    return write_output(source, destination, entries, paths, carriers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--recovery', type=Path, help='JSON object mapping exact native references to recovered integer Tiers')
    args = parser.parse_args()
    recovery = json.loads(args.recovery.read_text()) if args.recovery else {}
    if not isinstance(recovery, dict) or any(not isinstance(k, str) or type(v) is not int for k, v in recovery.items()):
        parser.error('Recovery must map exact references to integer Tiers')
    run(args.source, args.destination, recovery)


if __name__ == '__main__':
    main()
