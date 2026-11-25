"""Check named import ownership using resolved Realization Graph sites."""

from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path, PurePosixPath
import sys

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import check_code_access

from .code_access_occurrences import code_access_occurrences
from .source import capture
from .web_imports import _WEB


def _provider(site, sources):
    if site.status != "internal" or site.target_path is None:
        return None
    path = site.target_path
    if site.target_kind == "package":
        path = (PurePosixPath(path) / "__init__.py").as_posix()
    return path if path in sources else None


def _statement_sites(sites):
    statements = defaultdict(list)
    for site in sites:
        statements[site.source_path, site.line, site.column].append(site)
    return statements


def _forwarding(sources, statements):
    links = {}
    for path, source in sources.items():
        for exported, imported, line, column in source.forwarded:
            candidates = statements[path, line, column]
            if source.language == "python":
                candidates = [site for site in candidates if site.written.endswith(f" import {imported}")]
            if len(candidates) != 1:
                continue
            site = candidates[0]
            provider = _provider(site, sources)
            if provider is not None:
                symbol = site.unit if source.language == "python" else imported
                links[path, exported] = provider, symbol
    return links


def _owner(binding, links):
    visited = set()
    while binding in links:
        if binding in visited:
            return None
        visited.add(binding)
        binding = links[binding]
    return binding


def _named_web_uses(sources):
    named = defaultdict(set)
    for path, source in sources.items():
        for symbol, line, column in source.named_uses:
            named[path, line, column].add(symbol)
    return named


def check(sources, sites):
    """Yield imports whose named symbols pass through a foreign Package."""
    links = _forwarding(sources, _statement_sites(sites))
    named_web_uses = _named_web_uses(sources)
    for site in sites:
        provider = _provider(site, sources)
        if provider is None:
            continue
        names = (site.unit,) if site.unit is not None else named_web_uses[site.source_path, site.line, site.column]
        for name in sorted(names):
            owner = _owner((provider, name), links)
            if owner is not None and PurePosixPath(owner[0]).parent != PurePosixPath(provider).parent:
                yield site, name, owner


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    try:
        root = args.project_root.resolve(strict=True)
        sources = capture(root, None)
        _, sites = code_access_occurrences(root, sources, None)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"import ownership: {error}", file=sys.stderr)
        return 1
    failed = any(source.language in _WEB and source.status == "unsupported" for source in sources.values())
    if failed:
        print("import ownership: use the framework-local Node, TypeScript and Svelte parsers to check web imports",
              file=sys.stderr)
    for problem in check_code_access(None, sources, (), include_entry_bypasses=True):
        failed = True
        print(problem.reason, file=sys.stderr)
    for site, name, (owner, original) in check(sources, sites):
        failed = True
        package = PurePosixPath(owner).parent.as_posix()
        symbol = original if original is not None else PurePosixPath(owner).stem
        print(f"{site.source_path}:{site.line}:{site.column + 1}: {name} passes through {site.target_path}. "
              f"Import {symbol} from the defining Package's entry ({package}).", file=sys.stderr)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
