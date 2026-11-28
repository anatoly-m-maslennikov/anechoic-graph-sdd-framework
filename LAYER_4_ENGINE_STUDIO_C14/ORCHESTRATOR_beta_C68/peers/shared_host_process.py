"""Own isolated Kernel and Orchestrator peers for a shared-host Project."""

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from ORCHESTRATOR_beta_C68.peers.project_peers import open_project_peers


@contextmanager
def open_peers(selection, stop, warm_worker=None):
    root = Path(selection.root)
    manifest = Path(selection.manifest_path)
    if (
        root.resolve(strict=True) != root
        or manifest.resolve(strict=True) != manifest
    ):
        raise ValueError("project_declarations_stale")
    binding = {
        "root": str(root),
        "control_root": selection.control_relative.as_posix(),
        "manifest_path": manifest.relative_to(root).as_posix(),
        "manifest_sha256": selection.manifest_sha256,
        "project_prefix": selection.project_prefix,
    }
    runtime = selection.parameters.get("runtime", {})
    workbench = runtime.get("iwe_console", runtime.get("workbench", {}))
    with TemporaryDirectory(
        prefix="anechoic-beta-project-", dir="/tmp"
    ) as tmp:
        with open_project_peers(
            Path(tmp).resolve(),
            selection.instance_id,
            binding,
            stop,
            watch_code=workbench.get("import_graph") is not False,
            storage=workbench.get("storage", "disk"),
            journal_storage=runtime.get("journal", {}).get("storage", "files"),
            journal_relative=selection.parameters.get("paths", {}).get(
                "journal_root"
            ),
            result_ttl_seconds=workbench.get("result_ttl_seconds"),
            warm_worker=warm_worker,
        ) as peers:
            yield peers
