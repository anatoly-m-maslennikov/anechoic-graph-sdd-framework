"""Fixture projects for Code Access occurrence tests."""


def _write_named_imports(root):
    (root / "pkg").mkdir()
    (root / "pkg" / "__init__.py").write_text("")
    (root / "pkg" / "api.py").write_text("")
    (root / "client.py").write_text(
        "from pkg.api import first as one, second as two\n"
        "from pkg import api\n"
        "from pkg.api import *\n"
        "from missing import unknown\n"
        "import pkg\n"
        "import pathlib\n"
    )


def _write_child_projects(root):
    for child in ("first", "second"):
        project = root / child
        (project / "same").mkdir(parents=True)
        (project / "pyproject.toml").write_text(
            '[project]\nname = "' + child + '"\nversion = "1"\n'
        )
        (project / "uv.lock").write_text("")
        (project / "same" / "__init__.py").write_text("")
        (project / "client.py").write_text("import same\nimport only_second\n")
    (root / "second" / "only_second.py").write_text("")


def _write_separate_locks(root):
    for child, env in (
        ("LAYER_4_ENGINE_STUDIO_C14", "engine"),
        ("LAYER_5_USER_SETUP_C65", "setup"),
        ("LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "release"),
    ):
        (root / child).mkdir(parents=True, exist_ok=True)
        (root / child / "client.py").write_text("import engine_alias\n")
        project = root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72" / env
        project.mkdir(parents=True, exist_ok=True)
        (project / "pyproject.toml").write_text(
            '[project]\nname = "' + env + '"\n'
        )
        (project / "uv.lock").write_text(
            '[[package]]\nname = "engine-dist"\n' if env == "engine" else ""
        )
