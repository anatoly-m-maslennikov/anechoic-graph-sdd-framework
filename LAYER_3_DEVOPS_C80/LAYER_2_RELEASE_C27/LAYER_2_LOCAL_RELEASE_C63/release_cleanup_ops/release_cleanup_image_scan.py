"""Discover and purge verified test images."""

from pathlib import Path


def purge_test_images(root, runner, candidates, protected, cleanup, gate):
    removed = set()
    for image in sorted(candidates.keys() - protected):
        owner = candidates[image]
        try:
            candidate_root = Path(owner["org.anechoic.host_project_root"])
            with gate._candidate_checkout_lock(root, candidate_root):
                if any(
                    candidate == image
                    for _, candidate, _ in gate.open_artifacts(candidate_root)
                ):
                    continue
                metadata = gate.image_metadata(root, runner, image)
                tags = gate._test_tags(metadata)
                if not tags or not gate._has_owner(
                    metadata.Config.Labels, owner
                ):
                    raise ValueError("Test image role or ownership changed")
                if gate._container_references(root, runner, image):
                    cleanup.notes.append(
                        f"Test image {image} retained: "
                        "a container still uses it."
                    )
                    cleanup.pending = True
                    continue
                gate.run_docker(root, runner, "image", "rm", *tags)
                removed.add(image)
        except (
            OSError,
            RuntimeError,
            ValueError,
            gate.subprocess.TimeoutExpired,
        ):
            cleanup.pending = True
            cleanup.notes.append(
                f"Test image {image} retained: "
                "checkout busy or removal unverified."
            )
    _verify_purged(root, runner, removed, cleanup, gate)


def _verify_purged(root, runner, removed, cleanup, gate):
    if removed:
        try:
            remaining = gate._image_inventory(root, runner)
            cleanup.notes.extend(
                f"Purged test image {image}."
                for image in sorted(removed - remaining)
            )
            cleanup.notes.extend(
                f"Test image {image} still exists in Docker."
                for image in sorted(removed & remaining)
            )
            cleanup.pending |= bool(removed & remaining)
        except (
            OSError,
            RuntimeError,
            ValueError,
            gate.subprocess.TimeoutExpired,
        ):
            cleanup.pending = True
            cleanup.notes.append(
                "Docker test image removal could not be verified."
            )


def discover_images(root, runner, current_image, cleanup, gate):
    observed = list(
        dict.fromkeys(
            gate.run_docker(
                root,
                runner,
                "image",
                "ls",
                "--no-trunc",
                "--quiet",
                "--filter",
                f"label={gate.SCHEMA}=1",
            ).splitlines()
        )
    )
    if any(gate.IMAGE.fullmatch(image) is None for image in observed):
        raise ValueError("Docker cleanup identifiers are invalid")
    return _classify_images(
        root, runner, current_image, cleanup, gate, observed
    )


def _classify_images(root, runner, current_image, cleanup, gate, observed):
    owned, candidates = [], {}
    for image in observed:
        if image == current_image:
            continue
        try:
            metadata = gate.image_metadata(root, runner, image)
            labels = metadata.Config.Labels
            if gate._test_tags(metadata) and (
                gate._has_owner(labels, cleanup.owner)
                or gate._foreign_owner(labels, cleanup.owner)
            ):
                candidates[image] = labels
                continue
            if gate._has_owner(labels, cleanup.owner):
                cleanup.images.add(image)
                owned.append(image)
            elif gate._declares_owner(labels):
                cleanup.pending |= not gate._foreign_owner(
                    labels, cleanup.owner
                )
                cleanup.notes.append(
                    f"Image {image} retained: "
                    "foreign or incomplete declared ownership."
                )
            else:
                cleanup.pending = True
                cleanup.notes.append(
                    f"Image {image} retained without "
                    "Project ownership evidence."
                )
        except (
            OSError,
            RuntimeError,
            ValueError,
            gate.subprocess.TimeoutExpired,
        ):
            cleanup.pending = True
            cleanup.notes.append(
                f"Image {image} retained: ownership inspection failed."
            )
    return owned, candidates
