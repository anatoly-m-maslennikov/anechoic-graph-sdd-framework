"""Resolve one exact native Project binding per request on a private stream."""

from dataclasses import asdict
import json
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import discover_native_project, mcp_tool_blacklist, rebind_native_selection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ProjectSelectionError
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__shared import reviewed_native_model


def select_runtime_project(project_root, control_root=None, *, instance_id=None, host_root=None):
    """Select the active Manifest and validate any transported host identity."""
    selection = discover_native_project(
        project_root, control_root, manifest_validator=lambda: reviewed_native_model().validate_manifest,
    )
    if host_root is not None and instance_id is None:
        raise ProjectSelectionError("Host Project binding requires an explicit instance identity")
    if instance_id is not None:
        selection = rebind_native_selection(selection, instance_id, host_root=host_root)
    return selection


def project_tool_policy(parameters):
    """Return the Project's exclusions and release Tool activation."""
    blacklist = tuple(sorted(mcp_tool_blacklist(parameters)))
    releases = parameters.get("project_mcp", {}).get("release_workflows_enabled") is True
    return blacklist, releases


def pinned_project(binding):
    selection = select_runtime_project(
        binding.project_root, binding.control_root, instance_id=binding.instance_id,
        host_root=binding.host_project_root,
    )
    if selection.manifest_sha256 != binding.manifest_sha256:
        raise ValueError("Project binding changed")
    return selection


def _selection(encoded):
    value = json.loads(encoded)
    if (not isinstance(value, dict) or set(value) != {"project_root", "control_root", "instance_id", "host_root"}
            or not isinstance(value["project_root"], str)
            or any(value[key] is not None and not isinstance(value[key], str)
                   for key in ("control_root", "instance_id", "host_root"))):
        raise ProjectSelectionError("Invalid Project admission request")
    selection = asdict(select_runtime_project(**value))
    del selection["structure_snapshot"]
    selection["tool_blacklist"], selection["release_workflows_enabled"] = project_tool_policy(selection["parameters"])
    for key in ("root", "control_root", "control_relative", "manifest_path", "host_root"):
        if selection[key] is not None:
            selection[key] = str(selection[key])
    return selection


def main():
    for line in sys.stdin.buffer:
        try:
            response = {"result": _selection(line)}
        except ProjectSelectionError as error:
            response = {"error": {"code": "project_selection_error", "message": str(error)}}
        except ValueError:
            response = {"error": {"code": "project_selection_error", "message": "Invalid Project admission request"}}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
