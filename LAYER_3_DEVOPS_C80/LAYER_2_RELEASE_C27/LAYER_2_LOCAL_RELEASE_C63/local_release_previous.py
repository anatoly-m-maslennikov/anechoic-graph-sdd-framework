"""Prove ownership before replacing the prior Project MCP container."""

import json
import re


def _remove_previous(
    root,
    identifier,
    row,
    candidate_image,
    cleanup,
    runner,
    cleanup_runner,
    image_labels,
):
    prior_id = row.get("Image", "")
    if prior_id == candidate_image:
        return (
            identifier,
            "Retained the exact candidate Project MCP container for canonical reuse.",
            False,
        )
    image_labels(root, cleanup_runner, prior_id)
    cleanup.attempted.add(identifier)
    if row["State"]["Running"]:
        stopped = runner(("docker", "container", "stop", identifier), root)
        if getattr(stopped, "returncode", 1) != 0:
            return (
                None,
                "The proven prior Project MCP container was retained because stop failed.",
                True,
            )
    removed = runner(("docker", "container", "rm", identifier), root)
    if getattr(removed, "returncode", 1) == 0:
        return (
            None,
            f"Stopped and removed prior Project MCP container {identifier} with exact Project labels.",
            False,
        )
    return (
        None,
        "A proven prior Project MCP container was retained because removal failed.",
        True,
    )


def _inspect_previous(
    root,
    selection,
    identifier,
    prior_project,
    candidate_image,
    cleanup,
    runner,
    cleanup_runner,
    image_labels,
):
    try:
        inspected = runner((
            "docker", "container", "inspect", "--format",
            '{"Image":{{json .Image}},"State":{"Running":{{json .State.Running}}},'
            '"Config":{"Labels":{{json .Config.Labels}}}}', identifier,
        ), root)
        row = json.loads(getattr(inspected, "stdout", ""))
        labels = row.get("Config", {}).get("Labels") if isinstance(row, dict) else None
        if (getattr(inspected, "returncode", 1) == 0 and isinstance(labels, dict)
                and labels.get("org.anechoic.project") == prior_project
                and labels.get("org.anechoic.service") == "mcp-http"
                and labels.get("org.anechoic.control_root") == selection.control_relative.as_posix()
                and labels.get("org.anechoic.host_project_root") == str(root)
                and isinstance(row.get("State"), dict) and isinstance(row["State"].get("Running"), bool)):
            return _remove_previous(root, identifier, row, candidate_image, cleanup, runner,
                                    cleanup_runner, image_labels)
        return None, "A prior Project MCP container was retained because its exact stopped ownership was not proven.", True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None, "A prior Project MCP container was retained because inspection was unavailable.", True


def previous_container(root, selection, prior_project, candidate_image, cleanup, runner,
                       cleanup_runner, image_labels, default_note):
    if prior_project is None:
        return None, default_note, False
    try:
        result = runner(("docker", "ps", "--all", "--no-trunc", "--filter",
                         f"label=org.anechoic.project={prior_project}", "--format", "{{.ID}}"), root)
    except OSError:
        result = None
    identifiers = (
        [
            value
            for value in getattr(result, "stdout", "").splitlines()
            if re.fullmatch(r"[0-9a-f]{12,64}", value)
        ]
        if getattr(result, "returncode", 1) == 0
        and isinstance(getattr(result, "stdout", ""), str)
        else []
    )
    if getattr(result, "returncode", 1) != 0:
        return None, "A prior Project MCP container was retained because discovery was unavailable.", True
    if len(identifiers) > 1:
        return None, "Prior Project MCP containers were retained because ownership was ambiguous.", True
    if identifiers and identifiers[0] in cleanup.attempted:
        return (
            None,
            f"Prior container {identifiers[0]} retained after its earlier removal attempt; no retry.",
            True,
        )
    if identifiers:
        return _inspect_previous(
            root,
            selection,
            identifiers[0],
            prior_project,
            candidate_image,
            cleanup,
            runner,
            cleanup_runner,
            image_labels,
        )
    return None, default_note, False
