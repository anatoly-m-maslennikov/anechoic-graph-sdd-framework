# Generalized case families

These families describe reusable invariant candidates. They do not claim that all 29 cases are broad scanners. Each analyzer must state its supported source shapes and facts. Report unsupported paths as unresolved so that coverage limits remain explicit.

## Input domains and normalization

- **Cases** `carrier-crlf-bounds`, `release-test-fixed-port`, `first-summary-survives-duplicate`, `saved-query-rebuild`.
- **Rule** Accept the specified input domain and preserve meaning across permitted representations.
- **Facts** Valid bounds and line endings; accepted port range; record selection and source preservation; identifier comparison rules.
- **Counterexample** A valid port other than one hardcoded value is rejected, or identifiers that differ only in case do not match.

## Namespace, scope, and visibility

- **Cases** `duckdb-primary-catalog`, `namespace-import-analysis`, `excluded-watch-roots`, `preserved-methodology-archive`.
- **Rule** Apply each lookup, traversal, watch, or verification only to its intended scope, while retaining eligible members.
- **Facts** Current catalog; import binding forms; exclusion and recursive coverage; package inclusion rules.
- **Counterexample** A lookup accepts a matching object from an attached catalog, or an excluded directory remains under a recursive watch.

## Identity and projection

- **Cases** `derived-ref-id`, `renumbered-legacy-alias`, `native-direct-update-response`, `local-release-result`, `watcher-receipt-projection`.
- **Rule** Derive and project the identity and public result required by the current state and its witnesses.
- **Facts** Current identity, version and status; alias uniqueness and path binding; response contract; run identity; receipt witness.
- **Counterexample** A state change leaves a stale reference ID, or a valid witnessed directory event is not recognized.

## Phase order and consumption

- **Cases** `e2e-editor-before-query`, `local-release-lock-before-mutation`, `saved-query-stale-table-rebuild`, `descendant-cancellation`.
- **Rule** Establish each required precondition or prior result before a dependent action consumes it.
- **Facts** Input value and dispatch order; lock and mutation order; table binding dependencies; parent and child state.
- **Counterexample** A dependent query materializes before its rebuilt input is bound, or a parent is canceled before its unfinished child.

## Progress and admissible transitions

- **Cases** `carrier-read-error-retry`, `first-spec-publication`, `migration-pinned-spec-publication`, `supervisor-manifest-repair`, `watcher-queue-wakeup`, `workflow-guard-validation`.
- **Rule** Admit valid transitions and retry recoverable work. When required by the contract, each admitted reachable state must have a path to an allowed final state; reject overlapping guards within the modeled scope.
- **Facts** Prior read error and source existence; publication prerequisites and pinning; retry and queue conditions; guards and final-state reachability.
- **Counterexample** An unchanged source with a prior read error is skipped, or a reachable closed workflow cycle has no path to a final state.

## Resource and effect budgets

- **Cases** `docker-watcher-process-exhaustion`, `duplicate-capture-currentness`, `promotion-unchanged-rereads`.
- **Rule** Bound repeated work and side effects to those needed for the operation.
- **Facts** Observer mode and scheduling branches; capture completion checks; prior capture and carrier metadata.
- **Counterexample** One filtered root schedules a recursive watch for every eligible child, or unchanged carrier bodies are read again.

## Integration contracts

- **Cases** `native-compose-project`, `native-workbench-status`, `release-canary-backend-coupling`.
- **Rule** Preserve the required configuration, admission, dispatch, and dependency boundaries across components.
- **Facts** Selected project namespace; gateway registration and owner method; public MCP initialization dependencies.
- **Counterexample** A launcher receives no required Compose namespace, or the public canary imports the Engine MCP backend.

## Evidence and limits

Old/fixed replay measures recall on recorded examples and whether the target clears on the recorded fix. Held-out seeded controls test specified variations outside those examples. New historical or live findings need independent confirmation; an analyzer indication alone is not a confirmed defect.

Five pilots target these rules within their supported source shapes and inputs:

- Check the exact intended browser input value before dispatch.
- Accept integer ports from 1 through 65535.
- Preserve release result identity and diagnostic fields.
- Bind rebuilt saved-query results before dependents consume them, across supplied dependency graphs.
- Reject overlapping workflow guards and require a path to an allowed final state from each admitted reachable state in supplied finite configurations.

Evidence is limited to historical examples and seeded controls. These pilots do not establish arbitrary source coverage or broad scanner coverage for the other cases.
