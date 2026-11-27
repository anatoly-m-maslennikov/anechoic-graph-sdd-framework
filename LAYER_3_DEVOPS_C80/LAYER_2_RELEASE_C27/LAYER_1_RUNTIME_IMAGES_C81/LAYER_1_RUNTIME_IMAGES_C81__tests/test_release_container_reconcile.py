"""Production container startup and ownership checks."""

from hashlib import sha256
import json
import subprocess

from LAYER_1_RUNTIME_IMAGES_C81.release_container import start_container
from LAYER_1_RUNTIME_IMAGES_C81.release_assets import LocalReleaseError


from ._container_fixture import ContainerFixture


class ContainerTests(ContainerFixture):
    def test_failed_candidate_notes_safe_diagnostics_before_removal(
        self,
    ):
        self.stop_candidate()
        self.row["Config"]["Env"] = ["TOKEN=never-store-this"]
        event = json.dumps(
            {
                "severity": "ERROR",
                "event": "startup_failed",
                "details": {"token": "never-store-this"},
                "reason": "never-store-this",
            }
        )
        self.logs = "\n".join([event] * 20 + ["unstructured never-store-this"])
        evidence = {}
        with self.assertRaisesRegex(
            LocalReleaseError, "local-release-container-exited"
        ) as raised:
            self.start(evidence)
        self.assertEqual({}, evidence)
        self.assertIn(
            ("docker", "logs", "--tail", "20", self.identifier),
            self.calls[:-1],
        )
        self.assertEqual(
            ("docker", "container", "rm", "-f", self.identifier),
            self.calls[-1],
        )
        note = raised.exception.__notes__[-1]
        self.assertNotIn("never-store-this", note)
        details = json.loads(
            note.removeprefix("Local Release startup diagnostics: ")
        )
        self.assertEqual(18092, details["loopback_port"])
        self.assertEqual(self.identifier, details["container_id"])
        self.assertEqual(137, details["state"]["exit_code"])
        self.assertTrue(details["state"]["oom_killed"])
        self.assertEqual(
            [{"severity": "ERROR", "event": "startup_failed"}] * 10,
            details["recent_events"],
        )

    def test_failed_adoption_with_wrong_owner_omits_container_logs(self):
        self.row["Config"]["Labels"]["org.anechoic.project"] = "e" * 64
        with self.assertRaisesRegex(
            LocalReleaseError, "local-release-container-identity-mismatch"
        ) as raised:
            start_container(
                self.root,
                self.selection,
                self.image,
                self.fingerprint,
                18092,
                self.run_docker,
                existing_container=self.identifier,
            )
        self.assertEqual(
            [("docker", "container", "inspect")] * 2,
            [call[:3] for call in self.calls],
        )
        self.assertIn(
            "container ownership unverified", raised.exception.__notes__[-1]
        )

    def test_failed_port_binding_reports_only_safe_cause_and_requested_port(
        self,
    ):
        def docker(argv, root):
            return subprocess.CompletedProcess(
                argv, 125, "", "bind: address already in use; never-store-this"
            )

        with self.assertRaisesRegex(
            LocalReleaseError, "local-release-container-command-failed"
        ) as raised:
            start_container(
                self.root,
                self.selection,
                self.image,
                self.fingerprint,
                18092,
                docker,
            )
        notes = "\n".join(raised.exception.__notes__)
        self.assertIn("Docker could not bind the requested port.", notes)
        self.assertIn('"loopback_port":18092', notes)
        self.assertNotIn("never-store-this", notes)

    def test_failed_bind_reconciles_only_proven_stopped_run_candidate(self):
        run_id = "failed-bind"
        label = "org.anechoic.local_release_run"
        label_value = sha256(run_id.encode()).hexdigest()

        docker = self._failed_bind_docker(label, label_value)

        for mode in ("owned-created", "wrong-owner", "owned-running"):
            with self.subTest(mode=mode):
                self.setUp()
                labels = self.row["Config"]["Labels"]
                labels[label] = (
                    label_value if mode != "wrong-owner" else "e" * 64
                )
                if mode != "owned-running":
                    self.stop_candidate()
                    self.row["State"]["Status"] = "created"
                with self.assertRaises(LocalReleaseError):
                    start_container(
                        self.root,
                        self.selection,
                        self.image,
                        self.fingerprint,
                        18092,
                        docker,
                        run_id=run_id,
                    )
                removals = [
                    call
                    for call in self.calls
                    if call[:3] == ("docker", "container", "rm")
                ]
                if mode == "owned-created":
                    self.assertIn(
                        ("docker", "logs", "--tail", "20", self.identifier),
                        self.calls[:-1],
                    )
                    self.assertEqual(
                        [("docker", "container", "rm", self.identifier)],
                        removals,
                    )
                else:
                    self.assertEqual([], removals)

    def test_invalid_input_runs_no_docker(self):
        with self.assertRaises(LocalReleaseError):
            start_container(
                self.root,
                self.selection,
                "latest",
                self.fingerprint,
                18092,
                self.run_docker,
            )
        self.assertEqual([], self.calls)
