"""Read exact Atom bindings for inventoried realization owners."""

from pathlib import Path
import os
import re
import sys

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        UniqueSafeLoader,
        check_yaml_resources,
    )  # fmt: skip
from .source import _event_path, _git_ignored, _relative, excluded_source_path

PIN = re.compile(r"([A-Z]+-[SP]-[0-9]+)@([0-9]+)")
SUFFIX = ".spec_trace.md"
PACKAGE_SUFFIX = "__spec_bind.yaml"


def _yaml_entries(content):
    check_yaml_resources(content)
    data = yaml.load(content, Loader=UniqueSafeLoader)
    if not isinstance(data, dict) or set(data) - {"implements", "applies"}:
        raise ValueError("expected a mapping with implements and applies keys")
    entries = []
    for section, values in data.items():
        if not isinstance(values, list):
            raise ValueError(
                f"{section} must be a list of exact Atom version pins"
            )
        entries.extend((section, value, None) for value in values)
    return entries


def _markdown_entries(content, kind):
    entries = []
    section = None
    for number, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line == "## Implements" or (
            line == "## Applies" and kind == "package"
        ):
            section = line.removeprefix("## ").lower()
            continue
        entries.append(
            (section, line[2:] if line.startswith("- ") else None, number)
        )
    return entries


def _validated_entries(entries):
    pins = []
    for section, value, number in entries:
        match = PIN.fullmatch(value) if isinstance(value, str) else None
        version = match.group(2).lstrip("0") if match else ""
        if (
            not section
            or not version
            or len(version) > 10
            or int(version) > 2_147_483_647
        ):
            location = f":{number}" if number is not None else ""
            raise ValueError(
                f"{location}: expected a heading or an exact Atom version pin"
            )
        pins.append((section, match.group(1), int(version)))
    return pins


def _read_pins(root, path, sidecar, kind):
    try:
        content = sidecar.read_text(encoding="utf-8")
        entries = (
            _yaml_entries(content)
            if sidecar.name.endswith(PACKAGE_SUFFIX)
            else _markdown_entries(content, kind)
        )
        return [
            (
                path.relative_to(root).as_posix(),
                sidecar.relative_to(root).as_posix(),
                *pin,
            )
            for pin in _validated_entries(entries)
        ]
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        print(
            f"Invalid spec trace {sidecar}{exc}"
            if str(exc).startswith(":")
            else f"Invalid spec trace {sidecar}: {exc}",
            file=sys.stderr,
        )
        return None


def is_trace_path(relative):
    return isinstance(relative, str) and (
        relative.endswith(PACKAGE_SUFFIX) or relative.endswith(SUFFIX)
    )


def _candidate_traces(root, candidates, ignored, strict):
    rows, states = [], {}
    for owner, kind, canonical, fallback in candidates:
        owner_relative = owner.relative_to(root).as_posix()
        if kind == "package":
            states[owner_relative] = "missing"
        for sidecar in (canonical, fallback):
            if sidecar is None:
                continue
            relative = sidecar.relative_to(root).as_posix()
            if relative in ignored:
                continue
            if os.path.lexists(sidecar):
                pins = None
                if (
                    _event_path(root, relative) is not None
                    and sidecar.is_file()
                ):
                    pins = _read_pins(root, owner, sidecar, kind)
                    rows.extend(pins or [])
                if strict and pins is None:
                    raise ValueError(f"Invalid spec trace {sidecar}")
                if kind == "package" and sidecar == canonical:
                    states[owner_relative] = (
                        "invalid"
                        if pins is None
                        else ("valid" if pins else "empty")
                    )
                break
    return rows, states


def native_trace_snapshot(root, nodes, *, strict=False):
    "Read trace rows and canonical Package binding states from one snapshot."
    root = Path(root).resolve()
    candidates = []
    for _, kind, _, relative, _, _ in nodes:
        root_package = kind == "package" and relative == "."
        if (
            kind not in ("package", "module")
            or not relative
            or (not root_package and _relative(relative) != relative)
            or excluded_source_path(relative)
        ):
            continue
        owner = root if root_package else _event_path(root, relative)
        if owner is None or (
            not owner.is_dir() if kind == "package" else not owner.is_file()
        ):
            continue
        canonical = (
            owner / (owner.name + PACKAGE_SUFFIX)
            if kind == "package"
            else owner.with_name(owner.name + SUFFIX)
        )
        fallback = (
            owner / (owner.name + ".p" + SUFFIX) if kind == "package" else None
        )
        candidates.append((owner, kind, canonical, fallback))
    paths = {
        path.relative_to(root).as_posix()
        for _, _, canonical, fallback in candidates
        for path in (canonical, fallback)
        if path is not None
    }
    ignored = _git_ignored(root, paths)
    return _candidate_traces(root, candidates, ignored, strict)


def native_trace_rows(root, nodes):
    # fmt: off
    (
        "Read bindings for the local owners already inventoried by the "
        "Realization Graph."
    )
    # fmt: on
    return native_trace_snapshot(root, nodes)[0]
