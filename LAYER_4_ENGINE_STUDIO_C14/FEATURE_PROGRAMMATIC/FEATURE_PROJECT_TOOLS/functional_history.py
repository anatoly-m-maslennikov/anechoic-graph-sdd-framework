"""Select whole Functional test packages from recent suite reports."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import owned_temporary_root


def history_roots(root):
    target = os.environ.get("ANECHOIC_FUNCTIONAL_HISTORY_ROOT")
    if target and (not Path(target).is_absolute() or not Path(target).is_dir()):
        raise ValueError("Functional history root must be an absolute Project directory")
    return list(dict.fromkeys([root, *([Path(target)] if target else [])]))


def _package(path):
    parents = Path(path).parents
    return next((parent.as_posix() for parent in parents if parent.name.endswith("__tests")), None)


def _reports(root):
    for project in history_roots(root):
        directory = owned_temporary_root(project, "test_reports")
        for path in directory.glob("*.json"):
            try:
                if path.is_symlink():
                    continue
                record = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(record, dict):
                    continue
                started = datetime.fromisoformat(record["started_at"])
                if started.tzinfo is not None:
                    yield started.astimezone(timezone.utc), record
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                continue


def select_fast(root, modules, report):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    window = {"selected_at": now.isoformat(), "cutoff": cutoff.isoformat()}
    seed = os.environ.get("ANECHOIC_FUNCTIONAL_SAMPLE_SEED") or str(uuid4())
    packages = {_package(module.relative_to(root).as_posix()) for module in modules}
    if None in packages:
        raise ValueError("Functional module has no test Package")
    records = list(_reports(root))
    replay = [(started, r["functional_selection"]) for started, r in records
              if started <= now and isinstance(r.get("functional_selection"), dict)
              and r["functional_selection"].get("seed") == seed
              and all(isinstance(r["functional_selection"].get(key), list)
                      and all(isinstance(item, str) for item in r["functional_selection"][key])
                      for key in ("hot_packages", "sample_packages"))]
    if replay:
        selection = max(replay, key=lambda entry: entry[0])[1]
        hot = set(selection["hot_packages"]) & packages
        sample = set(selection["sample_packages"]) & packages
        window = {key: selection.get(key, value) for key, value in window.items()}
    else:
        hot = _hot_packages(records, cutoff, now) & packages
        remaining = packages - hot
        ordered = sorted(remaining, key=lambda path: (hashlib.sha256((seed + "\0" + path).encode()).digest(), path))
        sample = set(ordered[:(len(remaining) + 9) // 10])
    report["functional_selection"] = {
        "seed": seed, **window,
        "selected_packages": sorted(hot | sample), "hot_packages": sorted(hot),
        "sample_packages": sorted(sample),
    }
    selected = [module for module in modules if _package(module.relative_to(root).as_posix()) in hot | sample]
    report["functional_selection"]["selected_paths"] = [module.relative_to(root).as_posix() for module in selected]
    return selected


def _hot_packages(records, cutoff, now):
    hot = set()
    for started, record in records:
        if not cutoff <= started <= now:
            continue
        modules = record.get("modules")
        if not isinstance(modules, list):
            continue
        for module in modules:
            if isinstance(module, dict) and module.get("status") == "failed" and isinstance(module.get("path"), str):
                package = _package(module["path"])
                if package:
                    hot.add(package)
    return hot
