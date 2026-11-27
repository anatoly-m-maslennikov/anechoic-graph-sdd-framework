import importlib.util
from pathlib import Path

path = Path(__file__).parents[1] / "web_import_review.py"
spec = importlib.util.spec_from_file_location("web_import_review", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def review(root, texts, links=()):
    return module.web_import_review(root, texts, links)


def test_top_level_effects_only(tmp_path):
    rows = review(tmp_path, {"a.js": "start();\nfunction f() { hidden(); }\n"})
    assert len(rows) == 1
    assert rows[0][:5] == ("a.js", 1, 0, "web_module_evaluation", "unresolved")


def test_type_import_emit_and_unknown_config(tmp_path):
    text = "import type { A } from './a';\nimport { type B } from './b';\n"
    rows = review(tmp_path, {"x.ts": text})
    assert rows[0][4:] == ("confirmed", "erased declaration-level type import")
    assert rows[1][4] == "unresolved"
    (tmp_path / "tsconfig.json").write_text(
        '{"compilerOptions":{"module":"esnext", "verbatimModuleSyntax":true}}'
    )
    rows = review(tmp_path, {"x.ts": text})
    assert rows[1][4:] == (
        "confirmed",
        "compiler emit preserves module evaluation",
    )
    (tmp_path / "tsconfig.json").write_text(
        '{"extends":"./base", "compilerOptions":{"verbatimModuleSyntax":true}}'
    )
    assert review(tmp_path, {"x.ts": text})[1][4] == "unresolved"


def test_structural_cycle_is_unresolved(tmp_path):
    sources = {"a.mjs": "import './b.mjs';", "b.mjs": "import './a.mjs';"}
    links = [
        (
            "1",
            "module:a.mjs",
            "module:b.mjs",
            "./b.mjs",
            1,
            0,
            "internal",
            False,
        ),
        (
            "2",
            "module:b.mjs",
            "module:a.mjs",
            "./a.mjs",
            1,
            0,
            "internal",
            False,
        ),
    ]
    rows = review(tmp_path, sources, links)
    assert len(rows) == 2 and all(row[4] == "unresolved" for row in rows)


def test_esm_cycle_with_top_level_binding_read(tmp_path):
    sources = {
        "a.mjs": "import { x } from './b.mjs';\nconst y = x;",
        "b.mjs": "import './a.mjs';\nexport const x = 1;",
    }
    links = [
        (
            "1",
            "module:a.mjs",
            "module:b.mjs",
            "./b.mjs",
            1,
            0,
            "internal",
            False,
        ),
        (
            "2",
            "module:b.mjs",
            "module:a.mjs",
            "./a.mjs",
            1,
            0,
            "internal",
            False,
        ),
    ]
    rows = review(tmp_path, sources, links)
    assert rows[0][4] == "confirmed" and "uninitialized binding" in rows[0][5]
    assert rows[1][4] == "unresolved"


def test_modeled_effects_and_shadowed_console(tmp_path):
    rows = review(
        tmp_path,
        {
            "a.js": 'console.log("hi");',
            "b.js": 'const console = fake; console.log("hi");',
            "c.js": 'process.env.TEST = "yes";',
        },
    )
    assert [row[4] for row in rows] == ["confirmed", "unresolved", "confirmed"]


def test_untrusted_config_never_claims_emit(tmp_path):
    source = {"x.ts": "import { type B } from './b';"}
    cfg = tmp_path / "tsconfig.json"
    cfg.write_text('{"compilerOptions":{"verbatimModuleSyntax":false}}')
    assert review(tmp_path, source)[0][4] == "unresolved"
    cfg.unlink()
    outside = tmp_path.parent / (tmp_path.name + "-external.json")
    try:
        outside.write_text('{"compilerOptions":{"verbatimModuleSyntax":true}}')
        cfg.symlink_to(outside)
        assert review(tmp_path, source)[0][4] == "unresolved"
    finally:
        outside.unlink(missing_ok=True)


def test_commonjs_cycle_witness_and_harmless_read(tmp_path):
    import subprocess

    sources = {
        "a.cjs": (
            "const dep = require('./b.cjs');\n"
            "exports.out = dep.value.member;\n"
        ),
        "b.cjs": (
            "const dep = require('./a.cjs');\nexports.value = {member: 1};\n"
        ),
    }
    # fmt: off
    links = [
        ("1", "module:a.cjs", "module:b.cjs", "./b.cjs", 1, 12,
         "internal", False),
        ("2", "module:b.cjs", "module:a.cjs", "./a.cjs", 1, 12,
         "internal", False),
    ]
    rows = review(tmp_path, sources, links)
    assert any(row[0] == "a.cjs" and row[1] == 2
               and row[4] == "confirmed" and "entering b.cjs" in row[5]
               for row in rows)
    for name, text in sources.items():
        (tmp_path / name).write_text(text)
    assert subprocess.run(["node", "b.cjs"], cwd=tmp_path,
                          capture_output=True).returncode != 0
    assert subprocess.run(["node", "a.cjs"], cwd=tmp_path,
                          capture_output=True).returncode == 0
    # fmt: on
    sources["a.cjs"] = sources["a.cjs"].replace(
        "dep.value.member", "dep.value"
    )
    (tmp_path / "a.cjs").write_text(sources["a.cjs"])
    assert (
        subprocess.run(
            ["node", "b.cjs"], cwd=tmp_path, capture_output=True
        ).returncode
        == 0
    )
    assert not any(
        row[4] == "confirmed" for row in review(tmp_path, sources, links)
    )


def load_tests(loader, tests, pattern):
    """Expose the path-based fixtures to unittest discovery."""
    import tempfile
    import unittest

    def run_fixture(fixture):
        with tempfile.TemporaryDirectory() as directory:
            fixture(Path(directory))

    suite = unittest.TestSuite()
    for name, fixture in sorted(globals().copy().items()):
        if name.startswith("test_") and callable(fixture):
            suite.addTest(
                unittest.FunctionTestCase(
                    lambda f=fixture: run_fixture(f), description=name
                )
            )
    return suite
