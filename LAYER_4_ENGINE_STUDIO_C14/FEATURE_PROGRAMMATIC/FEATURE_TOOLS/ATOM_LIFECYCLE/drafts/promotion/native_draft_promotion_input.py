"""Validate Draft promotion inputs."""


def _promotion_input(selection, params):
    from . import native_draft_promotion__shared as promotion

    if not isinstance(params, dict) or set(params) != {
        "target",
        "targetStatus",
    }:
        raise promotion.common.InputError(
            "target", "Supply an exact Draft target and Current Status."
        )
    target, status = params["target"], params["targetStatus"]
    if (
        not isinstance(target, dict)
        or set(target) != {"ref_id", "version"}
        or not isinstance(target["ref_id"], str)
        or type(target["version"]) is not int
        or target["version"] < 1
    ):
        raise promotion.common.InputError(
            "target", "Supply an exact Draft reference and Version."
        )
    match = promotion.re.fullmatch(
        (
            "("
            f"{promotion.re.escape(selection.project_prefix)}"
            "-[STPC]-[0-9]+)@([1-9][0-9]*)-draft"
        ),
        target["ref_id"],
    )
    if match is None or int(match[2]) != target["version"]:
        raise promotion.common.InputError(
            "target", "Supply an exact Draft reference and matching Version."
        )
    _validate_status(status, match)
    return target, status, match


def _validate_status(status, match):
    from . import native_draft_promotion__shared as promotion

    if (
        not isinstance(status, str)
        or status
        not in {
            "active",
            "ready",
            "in_queue",
            "backlog",
            "done",
            "canceled",
            "resolved",
        }
        or ("-S-" in match[1] and status != "ready")
        or (("-P-" in match[1] or "-C-" in match[1]) and status != "active")
        or ("-T-" in match[1] and status in {"ready", "in_queue"})
    ):
        raise promotion.common.InputError(
            "targetStatus", "Supply an applicable Current Status."
        )


def _is_custom_replacement(header):
    from . import native_draft_promotion__shared as promotion

    context = promotion.native_header_view(header).get("context", {})
    return (
        header.get("atom_family") == "PROJECT_CONFIG"
        and context.get("container") == {"component": "C00"}
        and context.get("template") == "manifest_node"
        and header.get("relations", {}).get("IS_REPLACEMENT_FOR")
    )
