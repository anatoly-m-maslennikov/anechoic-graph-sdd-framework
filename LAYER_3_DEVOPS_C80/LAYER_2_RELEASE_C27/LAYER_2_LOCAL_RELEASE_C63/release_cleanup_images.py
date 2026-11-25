"""Purge unused test images and retain the Project's production history."""


from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from tempfile import NamedTemporaryFile

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    Cleanup,
    IMAGE,
    SCHEMA,
    Runner,
    image_labels,
    image_metadata,
    run_docker,
)
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import INSTALLATION_LOCK_PATH

from .local_release_state import open_artifacts


_OWNER_KEYS = (
    "org.anechoic.project",
    "org.anechoic.control_root",
    "org.anechoic.host_project_root",
)
_BROWSER_TEST_PREFIXES = ("anechoic-browser-", "anechoic-verified-browser-")
_LEGACY_TEST_TAG = re.compile(
    r"anechoic-runtime:\d+(?:\.\d+)+-(?:test|beta(?:-next)?)-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}Z-"
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


def _test_tags(metadata) -> tuple[str, ...]:
    tags = tuple(metadata.RepoTags or ())
    candidates = {f"anechoic-runtime:{role}-{metadata.Id[7:]}" for role in ("test", "beta", "beta-next")}
    short_id = metadata.Id[7:19]
    if all(tag in candidates or tag.partition(":")[0].startswith(_BROWSER_TEST_PREFIXES)
           or (tag.endswith(short_id) and _LEGACY_TEST_TAG.fullmatch(tag[:-len(short_id)])) for tag in tags):
        return tags
    return ()


@contextmanager
def _candidate_checkout_lock(root: Path, candidate_root: Path):
    if candidate_root == root:
        yield
        return
    lock = candidate_root / INSTALLATION_LOCK_PATH
    if lock.resolve() != lock:
        raise ValueError("Candidate checkout lock path is unsafe")
    try:
        descriptor = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        yield
        return
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("Candidate checkout lock is not a file")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(descriptor)


def _container_references(root: Path, runner: Runner | None, image: str) -> bool:
    return bool(run_docker(
        root, runner, "container", "ls", "--all", "--filter", f"ancestor={image}", "--quiet"
    ).strip())


def _image_inventory(root, runner):
    images = set(run_docker(root, runner, "image", "ls", "--all", "--no-trunc", "--quiet").splitlines())
    if any(IMAGE.fullmatch(image) is None for image in images):
        raise ValueError("Docker cleanup identifiers are invalid")
    return images


def _purge_test_images(root, runner, candidates, protected, cleanup):
    removed = set()
    for image in sorted(candidates.keys() - protected):
        owner = candidates[image]
        try:
            candidate_root = Path(owner["org.anechoic.host_project_root"])
            with _candidate_checkout_lock(root, candidate_root):
                if any(candidate == image for _, candidate, _ in open_artifacts(candidate_root)):
                    continue
                metadata = image_metadata(root, runner, image)
                tags = _test_tags(metadata)
                if not tags or not _has_owner(metadata.Config.Labels, owner):
                    raise ValueError("Test image role or ownership changed")
                if _container_references(root, runner, image):
                    cleanup.notes.append(f"Test image {image} retained: a container still uses it.")
                    cleanup.pending = True
                    continue
                run_docker(root, runner, "image", "rm", *tags)
                removed.add(image)
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
            cleanup.pending = True
            cleanup.notes.append(f"Test image {image} retained: checkout busy or removal unverified.")
    if removed:
        try:
            remaining = _image_inventory(root, runner)
            cleanup.notes.extend(f"Purged test image {image}." for image in sorted(removed - remaining))
            cleanup.notes.extend(f"Test image {image} still exists in Docker." for image in sorted(removed & remaining))
            cleanup.pending |= bool(removed & remaining)
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
            cleanup.pending = True
            cleanup.notes.append("Docker test image removal could not be verified.")


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
    if _container_references(root, runner, image):
        cleanup.notes.append(f"Image {image} retained: a container still uses it.")
        cleanup.pending = True
        return
    run_docker(root, runner, "image", "rm", image)
    cleanup.notes.append(f"Removed obsolete Project-owned image {image}.")


def _discover_images(
    root: Path, runner: Runner | None, current_image: str, cleanup: Cleanup
) -> tuple[list[str], dict[str, dict[str, str]]]:
    observed = list(dict.fromkeys(
        run_docker(
            root, runner, "image", "ls", "--no-trunc", "--quiet", "--filter", f"label={SCHEMA}=1"
        ).splitlines()
    ))
    if any(IMAGE.fullmatch(image) is None for image in observed):
        raise ValueError("Docker cleanup identifiers are invalid")
    owned, candidates = [], {}
    for image in observed:
        if image == current_image:
            continue
        try:
            metadata = image_metadata(root, runner, image)
            labels = metadata.Config.Labels
            if _test_tags(metadata) and (_has_owner(labels, cleanup.owner) or _foreign_owner(labels, cleanup.owner)):
                candidates[image] = labels
                continue
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
    return owned, candidates


def _retain_previous_images(root, runner, history, present, protected, cleanup):
    retained = 0
    for image in history:
        if image is None or image in protected:
            continue
        protected.add(image)
        if IMAGE.fullmatch(image) and image not in present:
            cleanup.notes.append(f"Previous image {image} is absent from the selected Docker context.")
            continue
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
    return retained


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
    history = (*previous_images, previous_image)
    try:
        owned, candidates = _discover_images(root, runner, current_image, cleanup)
        present = _image_inventory(root, runner) if any(history) else set()
        active_images = {image for _, image, _ in open_artifacts(root) if isinstance(image, str)}
    except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
        cleanup.pending = True
        cleanup.notes.append("Runtime image discovery unavailable; unproven images retained.")
        return
    protected = {current_image}
    retained = _retain_previous_images(root, runner, history, present, protected, cleanup)
    for image in owned:
        if retained == 2:
            break
        if image not in protected:
            protected.add(image)
            retained += 1
    _purge_test_images(root, runner, candidates, protected, cleanup)
    for image in sorted(cleanup.images - protected - candidates.keys() - active_images):
        try:
            _remove_image(root, runner, image, current_image, cleanup)
        except OSError, RuntimeError, ValueError, subprocess.TimeoutExpired:
            cleanup.pending = True
            cleanup.notes.append(f"Image {image} retained: inspection or removal failed.")
