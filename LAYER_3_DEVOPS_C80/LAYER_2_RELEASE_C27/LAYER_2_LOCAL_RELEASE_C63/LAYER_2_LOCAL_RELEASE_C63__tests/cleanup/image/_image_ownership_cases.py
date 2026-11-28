"""Fake image inventory and image-ownership cases."""

import json
from pathlib import Path
import subprocess

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.cleanup import test_release_cleanup as fixtures
from LAYER_2_LOCAL_RELEASE_C63.release_cleanup import cleanup_obsolete_images
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    Cleanup,
    owner_labels,
)


class OwnedDocker(fixtures.DockerFixture):
    def __init__(self) -> None:
        super().__init__()
        self.metadata_overrides: dict[str, dict[str, str]] = {}

    def run(
        self, argv: tuple[str, ...], root: Path
    ) -> subprocess.CompletedProcess[str]:
        result = super().run(argv, root)
        if argv[1:3] == ("image", "inspect") and result.returncode == 0:
            value = json.loads(result.stdout)
            value["Config"]["Labels"].update(
                self.metadata_overrides.get(argv[-1], {})
            )
            result.stdout = json.dumps(value)
        return result


class ImageOwnershipCases:
    def test_unowned_orphan_and_linked_image_are_retained_pending(
        self,
    ) -> None:
        for linked in (False, True):
            with self.subTest(linked=linked):
                docker = OwnedDocker()
                image = "sha256:" + "1" * 64
                docker.images[image] = "1" * 64
                cleanup = Cleanup(
                    owner=owner_labels(
                        fixtures.ROOT, "c" * 64, ".anechoic_anechoic"
                    )
                )
                if linked:
                    cleanup.images.add(image)
                cleanup_obsolete_images(
                    fixtures.ROOT,
                    fixtures.CURRENT,
                    fixtures.FINGER,
                    cleanup,
                    docker.run,
                )
                self.assertTrue(cleanup.pending)
                self.assertNotIn(
                    ("docker", "image", "rm", image), docker.calls
                )

    def test_owned_image_with_container_use_is_preserved_pending(self) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        docker.images[image] = "1" * 64
        docker.references.add(image)
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        docker.metadata_overrides[image] = owner
        cleanup = Cleanup(owner=owner)
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
        )
        self.assertFalse(cleanup.pending)
        self.assertNotIn(("docker", "image", "rm", image), docker.calls)

    def test_verified_predecessors_take_priority_over_discovery_order(
        self,
    ) -> None:
        docker = OwnedDocker()
        images = ["sha256:" + char * 64 for char in "1234"]
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        for image in images:
            docker.images[image] = fixtures.FINGER
            docker.metadata_overrides[image] = owner
        cleanup = Cleanup(owner=owner)
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
            previous_images=(images[2], images[3]),
        )
        removed = {
            call[-1] for call in docker.calls if call[1:3] == ("image", "rm")
        }
        self.assertEqual(removed, set(images[:2]))

    def test_fallback_retains_first_two_owned_images_in_docker_order(
        self,
    ) -> None:
        docker = OwnedDocker()
        images = ["sha256:" + char * 64 for char in "321"]
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        for image in images:
            docker.images[image] = fixtures.FINGER
            docker.metadata_overrides[image] = owner
        cleanup = Cleanup(owner=owner)
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
        )
        removed = {
            call[-1] for call in docker.calls if call[1:3] == ("image", "rm")
        }
        self.assertEqual(removed, {images[2]})
