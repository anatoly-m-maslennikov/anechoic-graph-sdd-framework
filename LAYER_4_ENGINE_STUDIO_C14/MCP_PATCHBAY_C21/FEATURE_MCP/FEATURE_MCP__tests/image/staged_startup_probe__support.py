"""Status checks for a packaged startup probe."""

from . import staged_startup__support as source


class ProbeStatus:
    def start_container(self, root, image, name):
        return self.docker(
            "run",
            "--detach",
            "--pull=never",
            "--init",
            "--read-only",
            "--name",
            name,
            "--label",
            "anechoic.test=staged-startup",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=256m",
            "--pids-limit",
            "128",
            "--cpus",
            "1",
            "--publish",
            "127.0.0.1::8092",
            "--mount",
            f"type=bind,src={root},dst=/project",
            "--env",
            "ANECHOIC_RUNTIME_NAMESPACE=docker",
            "--env",
            f"ANECHOIC_CONTROL_ROOT={source.CONTROL}",
            "--env",
            f"ANECHOIC_PROJECT_INSTANCE_ID={self.instance}",
            "--env",
            f"ANECHOIC_HOST_PROJECT_ROOT={root}",
            "--env",
            source.docker_deadline_env(),
            "--env",
            "ANECHOIC_STARTUP_TIMING=1",
            "--entrypoint",
            "/opt/venv/bin/python",
            image,
            "-B",
            "-c",
            source._WRAPPER,
            timeout=45,
        )

    def health(self):
        return self.peer("db.sock", "GET", "/health")

    def jobs(self):
        return self.peer(
            "jobs.sock",
            "GET",
            "/jobs/worker-runs?instance_id=" + self.instance,
        )

    def rows(self, sql):
        return self.peer(
            "db.sock",
            "POST",
            "/database",
            {"instance_id": self.instance, "sql": sql},
        )["rows"]

    def archive_marker(self):
        return self.exec(
            (
                "from pathlib import Path; p=Path('/tmp/"
                "staged-archive-pid'); print(p.read_text() if p.exists() "
                "else '')"
            )
        )

    def stopped(self):
        marker = self.archive_marker()
        jobs = self.jobs()
        latest, archive = jobs.get("latest") or {}, jobs.get("archive") or {}
        if latest.get("state") in ("failed", "aborted") and not latest.get(
            "retrying"
        ):
            raise RuntimeError(
                "Startup failed before archive barrier: "
                + source.json.dumps(latest)
            )
        if archive.get("state") in ("failed", "aborted", "succeeded"):
            raise RuntimeError(
                "Archive terminated before barrier: "
                + source.json.dumps(archive)
            )
        if (
            not marker
            and not archive
            and latest.get("state") == "succeeded"
            and not self.health()["archive_pending"]
        ):
            raise RuntimeError(
                (
                    "Startup completed without scheduling the expected "
                    "archive Worker"
                )
            )
        return marker

    def release(self):
        self.exec(
            (
                "import os,signal; from pathlib import Path; p=Path('/tmp/"
                "staged-archive-pid'); os.kill(int(p.read_text()),signal."
                "SIGCONT); p.unlink()"
            )
        )

    def complete_unchanged(self):
        if self.archive_marker():
            self.release()
        return self.complete()

    def disk(self):
        return source.json.loads(self.exec(source._DB))

    def ready(self):
        health, jobs = self.health(), self.jobs()
        latest = jobs.get("latest") or {}
        if latest.get("state") == "failed" and not latest.get("retrying"):
            raise RuntimeError(str(latest))
        return (
            (health, jobs)
            if health["ready"] and latest.get("state") == "succeeded"
            else None
        )

    def complete(self):
        health, jobs = self.health(), self.jobs()
        archive = jobs.get("archive") or {}
        if archive.get("state") in ("failed", "aborted"):
            raise RuntimeError(str(archive))
        return (
            (health, jobs)
            if not health["archive_pending"]
            and archive.get("state") == "succeeded"
            else None
        )
