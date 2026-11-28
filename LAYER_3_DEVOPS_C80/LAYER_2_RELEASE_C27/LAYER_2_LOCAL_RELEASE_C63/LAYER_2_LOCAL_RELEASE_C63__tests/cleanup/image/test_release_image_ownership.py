"Owned orphan discovery never upgrades missing or foreign ownership claims."

from __future__ import annotations

import fcntl
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.cleanup.image import _image_ownership_cases as cases
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.cleanup import test_release_cleanup as fixtures
from LAYER_2_LOCAL_RELEASE_C63.release_cleanup import cleanup_obsolete_images
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    Cleanup,
    owner_labels,
)
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    INSTALLATION_LOCK_PATH,
)


OwnedDocker = cases.OwnedDocker


class ReleaseImageOwnershipTests(cases.ImageOwnershipCases, unittest.TestCase):
    def test_purges_unused_test_images_across_projects_and_keeps_production(
        self,
    ) -> None:
        docker = OwnedDocker()
        own_test, foreign_beta, prior, used, own_next = (
            "sha256:" + digit * 64 for digit in "12345"
        )
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        foreign = owner_labels(Path("/foreign"), "f" * 64, "_anechoic_foreign")
        own_tags = [f"anechoic-runtime:test-{own_test[7:]}"]
        beta_tags = [
            f"anechoic-runtime:beta-{foreign_beta[7:]}",
            "anechoic-browser-parity-app:fixture",
            f"anechoic-runtime:0.4.4.73-beta-2026-11-22_12-14-30Z-{foreign_beta[7:19]}",
        ]
        prior_tags = [
            f"anechoic-runtime:prod-{prior[7:]}",
            f"anechoic-runtime:beta-{prior[7:]}",
        ]
        used_tags = [f"anechoic-runtime:test-{used[7:]}"]
        next_tags = [
            f"anechoic-runtime:beta-next-{own_next[7:]}",
            f"anechoic-runtime:0.4.4.73-beta-next-2026-11-22_12-14-30Z-{own_next[7:19]}",
        ]
        for image, labels, tags in (
            (own_test, owner, own_tags),
            (foreign_beta, foreign, beta_tags),
            (prior, owner, prior_tags),
            (used, foreign, used_tags),
            (own_next, owner, next_tags),
        ):
            docker.images[image] = fixtures.FINGER
            docker.metadata_overrides[image] = labels
            docker.image_tags[image] = tags
        docker.references.add(used)
        self._assert_test_image_cleanup(
            docker, owner, prior, own_tags, beta_tags, next_tags
        )

    def _assert_test_image_cleanup(
        self, docker, owner, prior, own_tags, beta_tags, next_tags
    ):
        cleanup = Cleanup(owner=owner)
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
            previous_image=prior,
        )
        removals = {
            call[3:] for call in docker.calls if call[1:3] == ("image", "rm")
        }
        self.assertEqual(
            removals, {tuple(own_tags), tuple(beta_tags), tuple(next_tags)}
        )
        self.assertTrue(cleanup.pending)

    def test_retains_unused_candidate_during_another_checkout_release(
        self,
    ) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        with TemporaryDirectory() as directory:
            foreign_root = Path(directory).resolve()
            docker.images[image] = fixtures.FINGER
            docker.metadata_overrides[image] = owner_labels(
                foreign_root, "f" * 64, "_anechoic_foreign"
            )
            docker.image_tags[image] = [f"anechoic-runtime:beta-{image[7:]}"]
            lock = foreign_root / INSTALLATION_LOCK_PATH
            lock.parent.mkdir(parents=True)
            cleanup = Cleanup(owner=owner)
            with lock.open("w") as held:
                fcntl.flock(held, fcntl.LOCK_EX)
                cleanup_obsolete_images(
                    fixtures.ROOT,
                    fixtures.CURRENT,
                    fixtures.FINGER,
                    cleanup,
                    docker.run,
                )
        self.assertFalse(
            any(call[1:3] == ("image", "rm") for call in docker.calls)
        )
        self.assertTrue(cleanup.pending)

    def test_ready_predecessor_is_kept_and_older_owned_image_removed(
        self,
    ) -> None:
        docker = OwnedDocker()
        prior, older = ("sha256:" + char * 64 for char in ("1", "2"))
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        for image in (prior, older):
            docker.images[image] = fixtures.FINGER
            docker.metadata_overrides[image] = owner
        cleanup = Cleanup(owner=owner)
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
            previous_image=prior,
        )
        self.assertNotIn(("docker", "image", "rm", prior), docker.calls)
        self.assertNotIn(("docker", "image", "rm", older), docker.calls)
        self.assertFalse(cleanup.pending)

    def test_absent_predecessor_needs_no_cleanup_in_this_context(self) -> None:
        image = "sha256:" + "1" * 64
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        for inventory_fails in (False, True):
            with self.subTest(inventory_fails=inventory_fails):
                docker = OwnedDocker()
                if inventory_fails:
                    docker.fail = ("docker", "image", "ls", "--all")
                cleanup = Cleanup(owner=owner, images={image})
                cleanup_obsolete_images(
                    fixtures.ROOT,
                    fixtures.CURRENT,
                    fixtures.FINGER,
                    cleanup,
                    docker.run,
                    previous_image=image,
                )
                self.assertEqual(inventory_fails, cleanup.pending)
                self.assertFalse(
                    any(call[-1] == image for call in docker.calls)
                )

    def test_owned_orphan_removed_without_container_link_or_commit_gate(
        self,
    ) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        docker.images[image] = "1" * 64
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
        self.assertNotIn(("docker", "image", "rm", image), docker.calls)
        self.assertFalse(cleanup.pending)

    def test_unlabelled_partial_or_conflicting_owner_is_retained_pending(
        self,
    ) -> None:
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        for metadata in (
            {},
            {"org.anechoic.project": "c" * 64},
            {**owner, "org.anechoic.host_project_root": "/different"},
        ):
            for linked in (False, True):
                if linked and not metadata:
                    continue
                with self.subTest(metadata=metadata, linked=linked):
                    docker = OwnedDocker()
                    image = "sha256:" + "1" * 64
                    docker.images[image] = "1" * 64
                    docker.metadata_overrides[image] = metadata
                    cleanup = Cleanup(
                        owner=owner, images={image} if linked else set()
                    )
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

    def test_foreign_owned_image_retained_even_with_project_container_link(
        self,
    ) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        docker.images[image] = "1" * 64
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        docker.metadata_overrides[image] = owner_labels(
            Path("/foreign"), "f" * 64, "_anechoic_foreign"
        )
        cleanup = Cleanup(owner=owner, images={image})
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
        )
        self.assertFalse(cleanup.pending)
        self.assertNotIn(("docker", "image", "rm", image), docker.calls)

    def test_same_fingerprint_owned_rebuild_is_removed(self) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        docker.images[image] = fixtures.FINGER
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
        self.assertNotIn(("docker", "image", "rm", image), docker.calls)
        self.assertFalse(cleanup.pending)

    def test_exact_candidate_is_protected_but_same_fingerprint_rebuild_is_not(
        self,
    ) -> None:
        docker = OwnedDocker()
        image = "sha256:" + "1" * 64
        docker.images[image] = fixtures.FINGER
        owner = owner_labels(fixtures.ROOT, "c" * 64, ".anechoic_anechoic")
        docker.metadata_overrides[image] = owner
        cleanup = Cleanup(owner=owner, images={fixtures.CURRENT, image})
        cleanup_obsolete_images(
            fixtures.ROOT,
            fixtures.CURRENT,
            fixtures.FINGER,
            cleanup,
            docker.run,
        )
        self.assertNotIn(
            ("docker", "image", "rm", fixtures.CURRENT), docker.calls
        )
        self.assertNotIn(("docker", "image", "rm", image), docker.calls)


if __name__ == "__main__":
    unittest.main()
