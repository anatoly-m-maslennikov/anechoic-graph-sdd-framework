"""Temporary Local Release resume fixtures and cases."""

import json
import subprocess

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class LocalReleaseResumeCases1:
    def release(self, runner, *, resume=False, **options):
        return run_local_release(
            self.root,
            run_id=self.run_id,
            runner=runner,
            resume=resume,
            **options,
        )

    def failed_gate(self, runner, phase):
        def run(argv, cwd):
            observed = runner(argv, cwd)
            if self.gate(argv) == phase:
                return subprocess.CompletedProcess(
                    argv, 1, "fixture test failure", ""
                )
            return observed

        return run

    @staticmethod
    def gate(argv):
        if "--phase" in argv:
            return argv[argv.index("--phase") + 1]
        return None

    def gates(self, calls):
        return [
            phase for argv in calls if (phase := self.gate(argv)) is not None
        ]

    def assert_same_candidate_version(self, expected):
        self.assertIn('version = "0.4.1.1"', expected)
        self.assertEqual(expected, (self.root / "version.toml").read_text())

    def git(self, *args, check=True):
        return subprocess.run(
            (
                "git",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "commit.gpgSign=false",
                *args,
            ),
            cwd=self.root,
            capture_output=True,
            text=True,
            check=check,
        )

    def _record_running_container(self, argv, cwd, row, identifier):
        self.assertFalse(row, "resume tried to start a second container")
        self.assertEqual((self.image_id, "mcp-http"), argv[-2:])
        labels = dict(
            argv[index + 1].split("=", 1)
            for index, argument in enumerate(argv)
            if argument == "--label"
        )
        row.update(
            Id=identifier,
            Image=self.image_id,
            Config={"Labels": labels},
            State={
                "Running": True,
                "Status": "running",
                "Health": {"Status": "healthy"},
            },
            NetworkSettings={
                "Ports": {
                    "8092/tcp": [{"HostIp": "127.0.0.1", "HostPort": "12345"}]
                }
            },
            Mounts=[
                {
                    "Type": "bind",
                    "Source": str(cwd),
                    "Destination": "/project",
                    "RW": True,
                },
                {
                    "Type": "volume",
                    "Name": "anechoic-framework-db",
                    "Destination": "/var/lib/anechoic",
                    "RW": True,
                },
            ],
        )
        return subprocess.CompletedProcess(argv, 0, identifier, "")

    def running_container_fixture(self):
        runner, calls = self._runner()
        identifier = "e" * 64
        row = {}

        def run(argv, cwd):
            observed = runner(argv, cwd)
            if argv[:2] == ("docker", "run"):
                return self._record_running_container(
                    argv, cwd, row, identifier
                )
            if row and (
                argv[:2] == ("docker", "ps")
                or argv[:3] == ("docker", "container", "ls")
            ):
                labels = {
                    f"label={name}={value}"
                    for name, value in row["Config"]["Labels"].items()
                }
                matched = all(
                    arg in labels for arg in argv if arg.startswith("label=")
                )
                return subprocess.CompletedProcess(
                    argv, 0, identifier if matched else "", ""
                )
            if row and argv[:3] == ("docker", "container", "inspect"):
                self.assertEqual(identifier, argv[-1])
                output = (
                    row
                    if argv[-2] == "{{json .}}"
                    else {
                        "Image": row["Image"],
                        "Config": row["Config"],
                        "State": {"Running": True, "Status": "running"},
                    }
                )
                return subprocess.CompletedProcess(
                    argv, 0, json.dumps(output), ""
                )
            return observed

        return run, calls, row
