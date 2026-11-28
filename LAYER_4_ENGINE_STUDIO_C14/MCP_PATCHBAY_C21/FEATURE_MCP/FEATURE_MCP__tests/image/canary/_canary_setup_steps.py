"""Private Docker image test steps."""


class CanarySetupSteps:
    @classmethod
    def _prepare_canary_project(cls):
        from .. import test_native_import_graph_docker_e2e as original

        image = original.os.environ.get("ANECHOIC_IMAGE", "")
        if not original.re.fullmatch(r"sha256:[0-9a-f]{64}", image):
            raise RuntimeError(
                "ANECHOIC_IMAGE must be the immutable test image ID"
            )
        cls.root = original.Path(
            cls.enterClassContext(original.tempfile.TemporaryDirectory())
        ).resolve()
        original.subprocess.run(
            ["git", "init", "--quiet", str(cls.root)], check=True
        )
        control = "_anechoic_anechoic"
        original.write_manifest(
            cls,
            cls.root / control,
            component="C00",
            parameters={
                "project": {"root": {"prefix": "underscore"}},
                "runtime": {
                    "journal": {"storage": "duckdb"},
                    "workbench": {"storage": "disk", "import_graph": {}},
                },
            },
        )
        (cls.root / control / "001_TICKETS/TASKS").mkdir(parents=True)
        return control, image

    @classmethod
    def _write_canary_files(cls):
        from .. import test_native_import_graph_docker_e2e as original

        for name, contents in (
            ("app/__init__.py", ""),
            ("app/main.py", "import dep.helper\nimport dep.helper\n"),
            ("app/package.json", '{"name": "app"}\n'),
            ("app/frontend.js", ""),
            ("dep/__init__.py", ""),
            ("dep/helper.py", "VALUE = 1\n"),
        ):
            cls._write(name, contents)
        (cls.root / "app/app__tests").mkdir()
        (cls.root / "app/app__tests/test_app.py").write_text(
            "pass\n", encoding="utf-8"
        )
        name = f"anechoic-import-graph-canary-{original.uuid4().hex}"
        original.defer_container_cleanup(cls.addClassCleanup, name)
        return name

    @classmethod
    def _start_canary_container(cls, control, image, name):
        from .. import test_native_import_graph_docker_e2e as original

        cls.container = original.subprocess.check_output(
            [
                "docker",
                "run",
                "--detach",
                "--pull=never",
                "--init",
                "--name",
                name,
                "--label",
                "anechoic.test=import-graph-canary",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,size=256m",
                "--pids-limit",
                "128",
                "--cpus",
                "1",
                "--publish",
                "127.0.0.1::8092",
                "--volume",
                f"{cls.root}:/project:rw",
                "--env",
                "ANECHOIC_RUNTIME_NAMESPACE=docker",
                "--env",
                f"ANECHOIC_CONTROL_ROOT={control}",
                "--env",
                original.docker_deadline_env(),
                image,
                "mcp-http",
            ],
            text=True,
            timeout=original.image_timeout(60),
        ).strip()

    @classmethod
    def _wait_canary_schema(cls):
        from .. import test_native_import_graph_docker_e2e as original

        cls._wait_ready()
        deadline = original.monotonic() + 60
        while original.observing(cls.container, deadline):
            status, payload = original.request(
                cls.api + "/schema", method="POST", payload={}
            )
            if status == 200 and "import_nodes" in payload.get("tables", {}):
                break
            original.sleep(0.2)
        else:
            raise RuntimeError(
                "Canary Import Graph schema failed to become ready"
            )
