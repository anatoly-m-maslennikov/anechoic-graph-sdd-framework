"""Run the Worker command and report ingestion failures."""
import argparse
import json
import subprocess
import sys
import traceback

from .managed_parent import watch_managed_parent


def _ingestion_failure(error):
    issues = getattr(error, "ingestion_issues", None)
    if issues is not None:
        return {"source": "atom", "issues": issues}
    return {"source": "build", "issues": [{
        "relative_path": None, "code": getattr(error, "issue_code", "build_failed"),
        "message": str(error)[-8192:] or type(error).__name__, "atom_ref": None, "related_paths": [],
    }]}


def main(run):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-dir")
    args = parser.parse_args()
    request = None
    try:
        watch_managed_parent()
        request = json.load(sys.stdin)
        result = run(request, args.generation_dir)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        if args.generation_dir is None:
            print(str(error), file=sys.stderr)
        else:
            traceback.print_exc()
            if isinstance(request, dict) and {"binding", "reuse"} <= request.keys():
                failure = {"ingestion_failure": _ingestion_failure(error)}
                if getattr(error, "model_diagnostics", None):
                    failure["model_diagnostics"] = error.model_diagnostics
                graph_consistency = getattr(error, "graph_consistency", None)
                if graph_consistency is not None:
                    failure["graph_consistency"] = graph_consistency
                print(json.dumps(failure, ensure_ascii=False))
        return 1
    return 0

