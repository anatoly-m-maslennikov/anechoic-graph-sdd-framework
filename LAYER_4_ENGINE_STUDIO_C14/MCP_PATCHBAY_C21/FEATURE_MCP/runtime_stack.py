"""Select the Engine runtime stack."""

from functools import lru_cache
import os


@lru_cache(maxsize=1)
def runtime_stack():
    stack = os.environ.get("ANECHOIC_RUNTIME_STACK", "current")
    if stack not in ("current", "beta_next"):
        raise ValueError("Invalid Framework stack")
    return stack


def beta_runtime_arguments(selection, socket, workbench_storage=None, journal_storage=None):
    args = ["API_MIXER_beta_C91.API_MIXER_beta_C91__shared", "--socket", str(socket),
            "--project-root", str(selection.root), "--control-root", selection.control_relative.as_posix(),
            "--instance-id", selection.instance_id, "--manifest-sha256", selection.manifest_sha256,
            "--manifest-path", selection.manifest_path.relative_to(selection.root).as_posix(),
            "--project-prefix", selection.project_prefix, "--project-name", selection.project_name]
    runtime = selection.parameters.get("runtime", {})
    workbench = runtime.get("iwe_console", runtime.get("workbench", {}))
    profile = "ANECHOIC_RUNTIME_PROFILE" in os.environ
    if not profile:
        storage = workbench.get("storage", workbench_storage or "disk")
        journal = runtime.get("journal", {}).get("storage", journal_storage or "files")
        args += ["--workbench-storage", storage, "--journal-storage", journal]
    public_url = workbench.get("public_url")
    if isinstance(public_url, str) and public_url and "\0" not in public_url:
        args.append(f"--workbench-public-url={public_url}")
    journal_relative = selection.parameters.get("paths", {}).get("journal_root")
    if journal_relative is not None:
        if not isinstance(journal_relative, str):
            raise ValueError("paths.journal_root must be a relative path")
        args += ["--journal-relative", journal_relative]
    if "result_ttl_seconds" in workbench:
        ttl = workbench["result_ttl_seconds"]
        if type(ttl) is not int or ttl <= 0:
            raise ValueError("workbench.result_ttl_seconds must be a positive integer")
        args += ["--result-ttl-seconds", str(ttl)]
    if selection.host_root is not None:
        args += ["--host-root", str(selection.host_root)]
    if workbench.get("import_graph") is not False:
        args.append("--watch-code")
    for name in selection.tool_blacklist:
        args += ["--blacklist", name]
    return args
