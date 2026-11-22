"""Remove only verified unused Project-owned noncandidate runtime images."""


import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile

from .release_cleanup_identity import (
    Cleanup,
    IMAGE,
    SCHEMA,
    Runner,
    image_labels,
    run_docker,
)


_OWNER_KEYS = (
    "org.anechoic.project",
    "org.anechoic.control_root",
    "org.anechoic.host_project_root",
)


def read_ready_images(path: Path, project_id: str) -> list[str]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(payload, dict) or payload.get("project_id") != project_id
            or not isinstance(payload.get("images"), list) or len(payload["images"]) > 3
            or any(not isinstance(item, str) or IMAGE.fullmatch(item) is None for item in payload["images"])):
        raise ValueError("Local release image history is invalid")
    return payload["images"]


def record_ready_images(path: Path, project_id: str, current: str, previous: str | None) -> tuple[str, ...]:
    """Remember verified production images in deployment order."""
    history = read_ready_images(path, project_id)
    images = list(dict.fromkeys(image for image in (current, previous, *history) if image is not None))[:3]
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
        temporary = Path(output.name)
        json.dump({"project_id": project_id, "images": images}, output)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return tuple(images[1:])


def _has_owner(labels: dict[str, str], owner: dict[str, str]) -> bool:
    return all(key in owner and labels.get(key) == owner[key] for key in _OWNER_KEYS)


def _declares_owner(labels: dict[str, str]) -> bool:
    return any(
        key in labels
        for key in _OWNER_KEYS
    )


def _foreign_owner(labels: dict[str, str], owner: dict[str, str]) -> bool:
    project_id = labels.get("org.anechoic.project", "")
    root = labels.get("org.anechoic.host_project_root", "")
    control = labels.get("org.anechoic.control_root", "")
    return (
        bool(owner)
        and project_id != owner.get("org.anechoic.project")
        and re.fullmatch(r"[0-9a-f]{64}", project_id) is not None
        and Path(root).is_absolute()
        and ".." not in Path(root).parts
        and control.startswith((".anechoic_", "_anechoic_")) and len(control) > len(".anechoic_")
        and len(Path(control).parts) == 1
    )


def _remove_image(
    root: Path,
    runner: Runner | None,
    image: str,
    current_image: str,
    cleanup: Cleanup,
) -> None:
    if image == current_image:
        cleanup.notes.append(f"Image {image} retained: exact candidate image.")
        return
    labels = image_labels(root, runner, image)
    if not _has_owner(labels, cleanup.owner):
        if _declares_owner(labels):
            cleanup.pending |= not _foreign_owner(labels, cleanup.owner)
            cleanup.notes.append(
                f"Image {image} retained: foreign or incomplete declared ownership."
            )
        else:
            cleanup.pending = True
            cleanup.notes.append(f"Image {image} retained without Project ownership evidence.")
        return
    references = run_docker(
        root, runner, "container", "ls", "--all", "--filter", f"ancestor={image}", "--quiet"
    )
    if references.strip():
        cleanup.notes.append(f"Image {image} retained: a container still uses it.")
        cleanup.pending = True
        return
    run_docker(root, runner, "image", "rm", image)
    cleanup.notes.append(f"Removed obsolete Project-owned image {image}.")


def _discover_images(
    root: Path, runner: Runner | None, current_image: str, cleanup: Cleanup
) -> list[str]:
    observed = list(dict.fromkeys(
        run_docker(
            root, runner, "image", "ls", "--no-trunc", "--quiet", "--filter", f"label={SCHEMA}=1"
        ).splitlines()
    ))
    if any(IMAGE.fullmatch(image) is None for image in observed):
        raise ValueError("Docker cleanup identifiers are invalid")
    owned = []
    for image in observed:
        if image == current_image:
            continue
        try:
            labels = image_labels(root, runner, image)
            if _has_owner(labels, cleanup.owner):
                cleanup.images.add(image)
                owned.append(image)
            elif _declares_owner(labels):
                cleanup.pending |= not _foreign_owner(labels, cleanup.owner)
                cleanup.notes.append(
                    f"Image {image} retained: foreign or incomplete declared ownership."
                )
            else:
                cleanup.pending = True
                cleanup.notes.append(f"Image {image} retained without Project ownership evidence.")
        except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
            cleanup.pending = True
            cleanup.notes.append(f"Image {image} retained: ownership inspection failed.")
    return owned


def cleanup_obsolete_images(
    root: Path,
    current_image: str,
    fingerprint: str,
    cleanup: Cleanup,
    runner: Runner | None = None,
    *,
    previous_image: str | None = None,
    previous_images: tuple[str, ...] = (),
) -> None:
    try:
        owned = _discover_images(root, runner, current_image, cleanup)
    except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
        cleanup.pending = True
        cleanup.notes.append("Runtime image discovery unavailable; unproven images retained.")
        return
    protected = {current_image}
    retained = 0
    for image in (*previous_images, previous_image):
        if image is None or image in protected:
            continue
        protected.add(image)
        try:
            if not _has_owner(image_labels(root, runner, image), cleanup.owner):
                raise ValueError("Previous image ownership unproven")
            retained += 1
            cleanup.notes.append(f"Image {image} retained: verified Project ownership.")
        except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
            cleanup.pending = True
            cleanup.notes.append(f"Image {image} retained: previous image ownership unproven.")
        if retained == 2:
            break
    for image in owned:
        if retained == 2:
            break
        if image not in protected:
            protected.add(image)
            retained += 1
    for image in sorted(cleanup.images - protected):
        try:
            _remove_image(root, runner, image, current_image, cleanup)
        except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
            cleanup.pending = True
            cleanup.notes.append(f"Image {image} retained: inspection or removal failed.")
