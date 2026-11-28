"""Validate selection for a SPEC status change."""


def select_spec_status(host, selection, params, current_rows):
    if not isinstance(params, dict) or set(params) != {
        "target",
        "targetStatus",
    }:
        raise host.InputError(
            "target", "Supply one Current SPEC target and Status."
        )
    target, status = params["target"], params["targetStatus"]
    if (
        not isinstance(target, dict)
        or set(target) != {"ref_id", "version"}
        or not isinstance(target["ref_id"], str)
        or not host.re.fullmatch(
            host.re.escape(selection.project_prefix) + r"-S-[0-9]+",
            target["ref_id"],
        )
        or type(target["version"]) is not int
        or target["version"] < 1
        or status not in {"active", "archived"}
    ):
        raise host.InputError(
            "target", "Supply a SPEC reference, Version and applicable Status."
        )
    matches = [
        row
        for row in current_rows
        if row.get("ref") == target["ref_id"]
        and row.get("status_group") == "Current"
        and row.get("version") == target["version"]
    ]
    if len(matches) != 1:
        raise host.SourceChanged(
            "Current SPEC selection is missing, ambiguous, or stale."
        )
    selected = matches[0]
    if (selected.get("status"), status) not in {
        ("ready", "active"),
        ("active", "archived"),
    }:
        raise host.InputError(
            "targetStatus",
            "Only Ready to Active and Active to Archived are supported.",
        )
    return target, status, selected
