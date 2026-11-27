import json
import os
import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[4]
MODULE = (
    "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.code_to_lean"
)


def _tool(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{sys.executable}\n{body}")
    path.chmod(0o755)


def _install_tools(tmp_path):
    log = tmp_path / "calls.jsonl"
    joern = tmp_path / "joern"
    autoform = tmp_path / "autoform"
    bin_dir = tmp_path / "bin"
    record = (
        "import json, os, sys\n"
        "with open(os.environ['TEST_CALLS'], 'a') as f:\n"
        "    f.write(json.dumps([os.path."
        "basename(sys.argv[0]), *sys.argv"
        "[1:]]) + '\\n')\n"
    )
    _tool(joern / "joern-parse", record)
    _tool(
        joern / "joern",
        record + "from pathlib import Path\n"
        "out = next(arg[4:] for arg in sys.argv if arg.startswith('out='))\n"
        "Path(out).write_text('{}')\n",
    )
    _tool(
        autoform / "cartographer" / "render_lean.py",
        record + "from pathlib import Path\n"
        "Path(sys.argv[2]).write_text('-- autoform result\\n')\n",
    )
    (autoform / "cartographer" / "export_ast.sc").touch()
    _tool(
        bin_dir / "pastalean",
        record + "from pathlib import Path\n"
        "Path(sys.argv[sys.argv.index('--"
        "output') + 1]).write_text('-- pa"
        "stalean result\\n')\n",
    )
    (tmp_path / "sitecustomize.py").write_text(
        "import os, shutil\n"
        "original = shutil.which\n"
        "def checked(command, *args, **kwargs):\n"
        "    if command == 'pastalean':\n"
        "        open(os.environ['TEST_LOOKUPS'], 'a').write('pastalean\\n')\n"
        "    return original(command, *args, **kwargs)\n"
        "shutil.which = checked\n"
    )
    return log, joern, autoform, bin_dir


def _tools(tmp_path):
    log, joern, autoform, bin_dir = _install_tools(tmp_path)
    env = os.environ.copy()
    env.update(
        AUTOFORM_CHECKOUT=str(autoform),
        JOERN_HOME=str(joern),
        PATH=str(bin_dir) + os.pathsep + env.get("PATH", ""),
        TEST_CALLS=str(log),
        TEST_LOOKUPS=str(tmp_path / "lookups"),
        PYTHONPATH=os.pathsep.join([str(tmp_path), str(ENGINE)]),
    )
    return env, log


def _translate(tmp_path, env, sources, translator=None, digests=()):
    output = tmp_path / "output.lean"
    args = [
        sys.executable,
        "-B",
        "-m",
        MODULE,
        *map(str, sources),
        "--output",
        str(output),
    ]
    if translator:
        args += ["--translator", translator]
    for digest in digests:
        args += ["--sha256", digest]
    result = subprocess.run(
        args,
        cwd=ENGINE,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    return result, output


def _run(tmp_path, env, suffix=".py", translator=None):
    source = tmp_path / ("input" + suffix)
    source.write_text("x = 1\n")
    return _translate(tmp_path, env, [source], translator)


def _calls(log):
    return (
        [json.loads(line) for line in log.read_text().splitlines()]
        if log.exists()
        else []
    )
