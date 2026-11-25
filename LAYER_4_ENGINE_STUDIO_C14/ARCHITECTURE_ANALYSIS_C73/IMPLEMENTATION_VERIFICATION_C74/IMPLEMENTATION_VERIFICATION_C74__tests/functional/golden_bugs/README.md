# Golden bug corpus

See [generalized case families](generalized-cases.md) for reusable invariants and evidence limits.

Each case preserves historical code inputs for a found and fixed bug. Its `case.json` records the title, invariant, scope, before and fixed revisions, source paths, fixture filenames, and SHA-256 digests. The inputs are exact historical source files or explicitly identified historical slices.

Each case also lists frozen Lean demonstrations in `checks`. They test the stated invariant within the case scope. A check may specify an exact expected `stdout_suffix` for its `#eval` output. The runner verifies the input digests and runs the saved Lean files; it does not regenerate them.

The Python snippets are golden inputs for future translator checks. This runner does not execute them or establish that a translation matches Python. Passing a Lean check establishes only the bounded claim expressed in that frozen demonstration.

Run from the repository root: `UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv" uv run --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --offline --no-sync --no-env-file python -B -m unittest discover -s LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional -p test_golden_bugs.py`. Install Lean on `PATH` or set `LEAN_BIN` to its executable. Missing Lean is a test failure. Selected editor synthetic controls also require Node and the locked Workbench frontend TypeScript dependency in the verifier checkout.

The generalized release-result analyzer accepts `CHECKOUT --lean LEAN --file RELATIVE` to select a source file. The saved-query analyzer accepts `--case GRAPH.json` for a supplied dependency graph, and the workflow analyzer accepts `--scenario CONFIG.json` for a supplied finite configuration; both also require `CHECKOUT --lean LEAN`. Unsupported inputs remain unresolved.

## Historical checkout scan

To scan an existing historical checkout, run:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv" uv run --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --offline --no-sync --no-env-file python -B LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/historical_checkout_scan.py --checkout /path/to/checkout
```

The scanner runs each case whose `case.json` declares `"analyzer": "analyze.py"`. It passes the checkout and `--lean` executable to each analyzer. Set `LEAN_BIN` or put Lean on `PATH`. Each analyzer discovers its own applicable source and emits JSON with `findings` and `unresolved` lists. Findings contain `path` and `detail` strings.

Some JavaScript and TypeScript analyzers require `node` and the locked Workbench frontend dependencies, including TypeScript and Acorn, in the verifier checkout at `LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/node_modules`. They do not use dependencies from the historical checkout. The namespace-import analyzer accepts `TYPESCRIPT_PATH` pointing to `typescript.js`; other analyzers may require the frontend dependency path. Missing dependencies produce unresolved results. To select another test with the generalized editor analyzer, run its `analyze.py` with `CHECKOUT --lean LEAN --file RELATIVE --title TEXT`, where the file is relative to the checkout.

The case metadata records Git revision hashes and SHA-256 hashes for its saved source fixtures. Replay output records the revisions; scan and replay output do not generally include hashes of every analyzed source file. Verify archived source hashes separately. These bounded static checks do not require running Docker.

The scanner emits case-tagged findings and unresolved results, plus a separate list of cases without an analyzer and counts for each list. It removes only identical findings for the same case, path, and detail. Invalid metadata, analyzer failures, malformed output, and timeouts are unresolved. A finding or an empty result covers only the analyzer's stated scope; gaps and unresolved results prevent a complete corpus assessment. This scan does not prove correctness of all Python code.

To replay declared cases at their recorded before and fixed Git revisions, run:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv" uv run --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --offline --no-sync --no-env-file python -B LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/historical_checkout_replay.py --case docker-watcher-process-exhaustion
```

Omit `--case` to replay all declared cases. The command uses a temporary shared clone with sparse historical layer directories and leaves the source checkout untouched. It scans each revision with all available analyzers. It reports target findings and unresolved results, retains other findings as untriaged indications, and reports old-case recall and the maximum total and extra findings per analyzed checkout. It exits nonzero when a target is unresolved, missed before, or still reported fixed. Cases without analyzers are gaps, not successful replays.

For archived source snapshots, verify their hashes separately and pass the extracted directory to `--checkout`. Git replay uses recorded Git revisions only; it does not count archived snapshots as replayed revisions.
