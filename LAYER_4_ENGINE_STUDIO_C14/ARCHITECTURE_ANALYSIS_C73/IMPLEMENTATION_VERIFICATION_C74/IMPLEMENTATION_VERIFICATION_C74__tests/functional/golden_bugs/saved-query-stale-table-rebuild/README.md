The default case rebuilds A and B in that order, with B reading A. Supply `--case graph.json` to select a different full rebuild. The JSON has `order`, a list of unique query identities in rebuild order, and `edges`, pairs `[upstream, dependent]`. An edge states that the dependent reads the upstream stable table. The graph must be acyclic and contain at most 32 queries and 256 edges. Independent queries need no particular order. Optional `released` is a list of unique identities from `order`; it records which retained results are released and defaults to empty.

Use `--file path/from/checkout.py` for a moved source module; the default discovers one historical Workbench `query_store.py` or C59 `query_results.py`; multiple candidates are unresolved.

The model uses supplied dependencies; it does not parse or execute SQL. It supports the documented full-rebuild source shapes and successful effects. The extracted `_stage_result_replacement` helper is resolved from the same class and its body is checked for effects and bindings. Other branches, binding forms, and effect orders return `unresolved`. A finding identifies the edge whose dependent materializes before the upstream stable table is rebound.

Run the persistent controls from the repository root with the pinned Lean binary:

```sh
LEAN_BIN=/path/to/lean UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv" uv run --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --offline --no-sync --no-env-file python -B LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/golden_bugs/saved-query-stale-table-rebuild/test_analyze.py
```

The Lean program includes the `Formal Claim` Lean block from AN-S-1363 verbatim, then evaluates the extracted effects against it. The supplied order is the retained-result dictionary insertion order for the full rebuild; `reversed(self._results.items())` visits it in reverse when `reversed` is unshadowed; the recognized `or old.released` retention guard skips observed released results in a single loop; partial-selection behavior is outside this model. Missing or unsupported source effects remain unresolved.
