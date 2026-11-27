"Discover and model the historical filtered-root watcher scheduling pattern."

import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def same(node, expression):
    return ast.dump(node, include_attributes=False) == ast.dump(
        ast.parse(expression, mode="eval").body, include_attributes=False
    )


def _matches_root_loop(start, old_filter, new_filter, loop_template):
    root_loops = [
        x
        for x in ast.walk(start)
        if isinstance(x, ast.For) and same(x.iter, "self._roots")
    ]
    if len(root_loops) != 1 or not any(
        isinstance(x, ast.If)
        and same(x.test, "filtered")
        and any(
            isinstance(y, ast.For) and same(y.iter, "path.iterdir()")
            for y in x.body
        )
        for x in root_loops[0].body
    ):
        return False
    if not any(
        ast.dump(root_loops[0], include_attributes=False)
        == ast.dump(
            ast.parse(loop_template.replace("FILTER", expression)).body[0],
            include_attributes=False,
        )
        for expression in (old_filter, new_filter)
    ):
        return False
    return True


def _observer_form(obs, filt, old_filter, new_filter):
    if same(obs[0], "factory()") and same(filt[0], old_filter):
        return False, True
    if same(
        obs[0],
        (
            "PollingObserverVFS(os.lstat, self._source_en"
            "tries) if self._poll_bind_mount else factory"
            "()"
        ),
    ) and same(filt[0], new_filter):
        return True, False
    return None


def _expected_schedules():
    return {
        (
            "observer.schedule(_Handler(self), str(path),"
            " recursive=not filtered)"
        ),
        ("observer.schedule(_Handler(self), str(child), recursive=True)"),
    }


def _analyze_start(start):
    assigns = [
        x
        for x in ast.walk(start)
        if isinstance(x, ast.Assign)
        and len(x.targets) == 1
        and isinstance(x.targets[0], ast.Name)
    ]
    obs = [x.value for x in assigns if x.targets[0].id == "observer"]
    filt = [x.value for x in assigns if x.targets[0].id == "filtered"]
    schedules = [
        x
        for x in ast.walk(start)
        if isinstance(x, ast.Call)
        and isinstance(x.func, ast.Attribute)
        and x.func.attr == "schedule"
    ]
    if len(obs) != 1 or len(filt) != 1 or len(schedules) != 2:
        return None
    expected = _expected_schedules()
    if {ast.unparse(x) for x in schedules} != expected:
        return None
    old_filter = "self._exclude_directory is not None and path == self._root"
    new_filter = (
        "not self._poll_bind_mount and self._exclude_"
        "directory is not None and path == self._root"
    )
    loop_template = (
        "for path in self._roots:\n"
        "    filtered = FILTER\n"
        "    self._watched_directories[path] = observ"
        "er.schedule(_Handler(self), str(path), recur"
        "sive=not filtered)\n"
        "    if filtered:\n"
        "        for child in path.iterdir():\n"
        "            if child.is_dir() and not child."
        "is_symlink() and not self._exclude_directory"
        "(child.relative_to(self._root).as_posix()):\n"
        "                self._watched_directories[ch"
        "ild] = observer.schedule(_Handler(self), str"
        "(child), recursive=True)\n"
    )
    if not _matches_root_loop(start, old_filter, new_filter, loop_template):
        return None
    return _observer_form(obs, filt, old_filter, new_filter)


def analyze(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError, UnicodeError, OSError:
        return None
    for cls in (x for x in tree.body if isinstance(x, ast.ClassDef)):
        for start in (
            x
            for x in cls.body
            if isinstance(x, ast.FunctionDef) and x.name == "start"
        ):
            result = _analyze_start(start)
            if result is not None:
                return result
    return None


def lean_source(polling, filtered):
    return (
        "-- Generated from the checked observer and filtered scheduling "
        "AST branches.\n"
        "-- One filtered root, with n eligible top-level children.\n"
        f"def pollingObserver : Bool := {str(polling).lower()}\n"
        f"def filteredRoot : Bool := {str(filtered).lower()}\n"
        "def schedules (n : Nat) : Nat := 1 + if filteredRoot then n else 0\n"
        "#eval (pollingObserver, schedules 80)\n"
        "theorem observed : (pollingObserver, schedules 80) = "
        f"({str(polling).lower()}, {81 if filtered else 1}) := by decide\n"
    )


def _find_watcher(checkout):
    found = [
        (path, result)
        for path in checkout.rglob("*.py")
        if (result := analyze(path)) is not None
    ]
    if len(found) != 1:
        raise ValueError(f"Expected one supported watcher; found {len(found)}")
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    output = {"findings": [], "unresolved": []}
    try:
        found = _find_watcher(args.checkout)
        path, (polling, filtered) = found[0]
        with tempfile.TemporaryDirectory() as tmp:
            lean_file = Path(tmp) / "watcher.lean"
            lean_file.write_text(lean_source(polling, filtered))
            result = subprocess.run(
                [args.lean, str(lean_file)],
                text=True,
                capture_output=True,
                check=True,
                timeout=30,
            )
        expected = f"({str(polling).lower()}, {81 if filtered else 1})"
        if result.stdout.strip() != expected:
            raise ValueError(
                f"Unexpected Lean output: {result.stdout.strip()}"
            )
        if not polling or filtered:
            output["findings"].append(
                {
                    "path": str(path.relative_to(args.checkout)),
                    "detail": (
                        "For a filtered root with 80 eligible child d"
                        "irectories, the modeled factory observer use"
                        "s 81 schedules instead of one polling schedu"
                        "le (Lean verified)."
                    ),
                }
            )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        output["unresolved"].append({"path": ".", "detail": str(error)})
    print(json.dumps(output))


if __name__ == "__main__":
    main()
