---
atom_family: TKT
atom_id: AN-T-3919
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T16:40:34.256033+00:00'
---
## Summary

Apply the refactoring decisions

## Prerequisite

Start after [AN-T-3918](AN-T-3918-TASK--assess-all-import-violations.md)
records the rewrite and repair decisions.

## Work

Apply the decisions in the recorded order. Preserve supported contracts and verify behavior with the relevant tests.

- Route cross-Package imports through the owning Package `__shared` entry.
  Permit only the exact bypasses documented in the assessment and Realization
  Graph. Never use a production import from a directory ending in `__tests`.
- Enforce the existing source-linter limits of 300 lines per module and 45
  lines per function. Remove unused code and avoid forwarding wrappers.
- Use Pydantic for every structured Python model across the Project. Include
  internal domain and state models, process, CLI, API, configuration, IPC and
  persistence, external adapters, request and result models, and structured
  models in tests. Validate untrusted input on admission, validate once, and
  reuse accepted model instances. Structured models mean named record or
  object data. Keep plain scalar and collection operations ordinary. Keep
  AN-S-1913 as the governing reference.
- Convert all project-authored JavaScript to TypeScript, including frontend,
  tests, and tooling. Generated JavaScript output is unaffected.
- Run the authorized parallel Beta path. Keep the existing production
  selection `stack = "beta"` for C67-C71. Assign the candidate new Component
  IDs and names in the form `<name>_beta_<new id>`. Select the candidate with a
  distinct value of the same existing `stack` key. Produce independent
  candidate and production images. Keep the Current selection intact until
  cutover. Add no extra runtime switch.
- Compare supported Contracts and performance while Candidate and Current
  coexist. Explain every discrepancy before promotion. Candidate closure must
  pass before cutover.
- During each refactoring review, consider merging, promoting, or splitting
  Packages, sub-Components, and Component Seeds when ownership warrants it.
  Consider additional ordered sibling layers with strictly forward
  dependencies and narrower explicit `imports.only` allowlists. Consider
  consolidating repeated stable cross-cutting code in an existing or narrowly
  scoped base library when it removes real duplication, such as a shared error
  or diagnostic decorator. Preserve error Contracts. Do not add forwarding
  wrappers or speculative abstractions. These are review criteria, not a
  mandatory wholesale reshuffle.
- Run `enforce_source_languages = true` for Beta verification and eventual
  cutover. Run the existing Current baseline in report mode. Review ad-hoc
  structured records in addition to the mechanical checks for explicit model
  declarations and authored JavaScript.
- Run focused functional tests as each changed boundary lands. After the full
  refactoring, run the packaged end-to-end suite and the MCP canary once.
- Supply the exact verified revision and packaged evidence to the two
  [Spec tasks in AN-T-3917](../AN-T-3917-EPIC--total-refactoring.md#spec-task-queue).

## Acceptance

- The whole-Project Realization Graph and import lint report zero import
  violations, including production imports from directories ending in
  `__tests`. Require the zero result after retiring the superseded active
  source at cutover.
- The existing source linter reports no module over 300 lines and no function
  over 45 lines. No unused code or forwarding wrapper remains in the changed
  implementation, and supported behavior is preserved.
- Every structured Python model uses Pydantic, including internal domain and
  state, process, CLI, API, configuration, IPC and persistence, external
  adapter, request and result, and test models. Untrusted input is validated on
  admission. Accepted model instances are reused. Plain scalar and collection
  operations remain ordinary. No project-authored JavaScript remains outside
  TypeScript. Generated output is excluded.
- Focused functional tests pass for each changed boundary. The full packaged
  end-to-end suite and one final MCP canary pass after all changes.
- Candidate closure passes while Current coexists. Candidate and production
  images are independent. The existing selector uses `stack = "beta"` for
  C67-C71 and a distinct value for the candidate. Their supported Contracts and
  performance are compared. Every discrepancy is explained before promotion.
  Current remains in place until cutover, with no extra runtime switch. The
  strict `enforce_source_languages = true` gate passes for Beta and eventual
  cutover. Current report mode records its baseline.

## Progress

- The isolated rehearsal retired C70 source and active authority.
  `beta_next` uses C68/C82. Current routing and source closure passed.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/activation.YXIkwk/activation.json`
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/packaging/final-tests.log`
- Isolated Test Package denials fell from 30 to zero. Production denials
  and undeclared bypasses were zero. The intentional C74 CTS fixture
  stayed uncertain. Declared bypass semantics stayed the same. Two C81
  line moves tripped the exact-coordinate comparison. Strict source
  languages and 45/300 checks passed.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/whole-gate/interpretation.json`
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/whole-gate/source-lint-classified.json`
- The sealed, untagged `beta_next` image is `sha256:99f8ddd9298c61c9b84f0b0fe4c22fbbb401efab7831358658d07aefc78be936`.
  AN-S-4738@3 specifies the load and latency measures.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/candidate-seal.NVuurC/build-result.json`
  `$BB_THREAD_STORAGE/an-s-4738-load-latency/source-revision-v3.json`
- The real load probe on that image made all 500 Tickets queryable,
  first at 3.101 s and last at 21.104 s. Query P95 was 201, 638, and
  1,014 ms at idle, during Archive, and during the batch, with zero
  errors in 12 queries per condition. One file change reached SQL in
  5.789 s. The sampled peaks were one active Worker and 128 watcher
  queue entries. The receipt records CPU, peak memory, and block I/O.
  `$BB_THREAD_STORAGE/c21-generation-load/fresh-candidate-run/generation_load.json`
- The first packaged restart rebuilt after five offline path changes.
  C30 rejected the legacy fixture header and accepted the canonical
  equivalent. The corrected host replay used the same database for
  full, reused, and five-path native delta. It admitted the offline
  Archive change.
  `$BB_THREAD_STORAGE/c21-staged-startup-canonical-replay/c30-comparison.json`
  `$BB_THREAD_STORAGE/c21-staged-startup-canonical-replay/host-replay.json`
- The first canonical Docker replay exposed an Archive test barrier
  that mixed owner snapshots. The barrier check reproduced the false
  terminal result. With the canonical fixture and test barrier fixed,
  the same image passed full, reused (0 changes), and native delta
  (5 changes) on one flat database. The offline Archived row became
  visible at Archive delta admission. First queries took 58.229,
  13.629, and 13.722 s. The receipt includes cgroup counters.
  The full packaged suite and MCP canary are pending.
  `$BB_THREAD_STORAGE/c21-staged-startup-canonical-replay/barrier-interleaving-proof.json`
  `$BB_THREAD_STORAGE/c21-staged-startup-canonical-replay/same-candidate-untouched-inputs/staged_startup.json`
- The live C68 source now validates timing relay records with strict
  Pydantic and records safe watcher fence diagnostics. The sealed
  image retains its original source.
  `$BB_THREAD_STORAGE/c68-watcher-fence-logging-final.log`
- The guarded C61 audit covered 4,135 source paths with zero drift.
  Test Package denials fell from 45 to 32 with zero new denials. Retained
  C70 has 20 and C21 has 12. Production denials and static ownership
  findings were zero. Declared bypasses and the C74 uncertainty were
  unchanged.
  `$BB_THREAD_STORAGE/c61-integrated-final-45/summary.json`
  `$BB_THREAD_STORAGE/c61-integrated-final-45/comparison.json`
  `$BB_THREAD_STORAGE/c61-integrated-final-77/comparison.json`
- AN-T-3918 completed the original assessment. Its Done transition
  remains blocked by failed archive loading on the installed MCP.
  Read-only inspection found the older fatal `_check_capture` path.
  `$BB_THREAD_STORAGE/an-t-3919-final-progress/assessment-readiness.json`
  `$BB_THREAD_STORAGE/live-archive-check-3919/deployed-source.json`
- A real IPC fixture on current source admitted the valid Archive,
  preserved the broken-carrier issue, and recorded the misplaced
  Ticket only as an issue. Archive loading succeeded. The next
  lifecycle call passed the archive guard.
  `$BB_THREAD_STORAGE/live-archive-check-3919/current-source-ipc-regression.json`
- C16 Tools and Generate Entity Graph, C30 adapters, C68, C82, and C63/C81
  release test slices reached zero scoped denials. All 100 C68 tests passed.
  Existing declared bypasses stay outside cleanup scope.
  `$BB_THREAD_STORAGE/c68-test-entry/c68.log`
  `$BB_THREAD_STORAGE/c16-dormant-path-cleanup/verification.json`
  `$BB_THREAD_STORAGE/c16-entity-graph-test-access/summary.json`
  `$BB_THREAD_STORAGE/c30-test-entry/code-access-final.json`
  `$BB_THREAD_STORAGE/c68-test-entry/code-access-final.json`
  `$BB_THREAD_STORAGE/c82-test-closure-final/c82-comparison.json`
  `$BB_THREAD_STORAGE/release-c63-test-access/native-final.json`
- C69 reuses the admitted Model on graph-only changes and rechecks the
  pinned Lean runtime and library. All 18 focused tests passed. Lean
  witness capture added 0.453 s to the median in the local timing fixture.
  `$BB_THREAD_STORAGE/c69-lean-graph-refresh/final-tests.log`
  `$BB_THREAD_STORAGE/c69-lean-graph-refresh/final-overhead.json`
- The latest strict scan found five structured Python models, all in
  retained C70. It found zero Web and 45/300 findings. The comment gate
  passed in the preceding tranche. A historical C52 asset preserves
  C53 compatibility coverage.
  `$BB_THREAD_STORAGE/c61-integrated-final-45/source-lint-classified.json`
  `$BB_THREAD_STORAGE/c53-test-entry/summary.json`
  `$BB_THREAD_STORAGE/source-comments-3919/`
- A source change during a C61 read restarts graph analysis only. The Worker
  reuses the original compile or published Model and Structure. Five focused
  tests and two subprocess smokes passed.
  `$BB_THREAD_STORAGE/c61-guarded-read/tests.log`
  `$BB_THREAD_STORAGE/c61-guarded-read/worker-smoke.json`
- C21 reads shared host Settings without importing C45 or C70. Focused
  checks preserved legacy settings behavior. Current still uses its
  existing runtime roles.
  `$BB_THREAD_STORAGE/c21-retained-host-settings/legacy-parity.json`
  `$BB_THREAD_STORAGE/c21-retained-host-settings/native-scope.json`
- C68 owns Project peers and shared leases. C82 serves Tools without
  retaining Project state. The earlier sealed pair differs in source only
  by the selector. C21/C81 agree on backend selection, and the candidate
  has no C70.
  `$BB_THREAD_STORAGE/c68-cutover-pair.uunLYq8f/paired-build-plan.json`
  `$BB_THREAD_STORAGE/c68-cutover-pair.uunLYq8f/paired-build-results.json`
- The earlier smoke passed all six cases. Separate no-C70 host runs
  covered Workspace and peer cleanup, and the scoped C82 check passed
  pending-archive parity.
  `$BB_THREAD_STORAGE/packaged-peer-owner-smoke/receipt.json`
  `$BB_THREAD_STORAGE/no-c70-cutover-verification/receipt.json`
- Real C68 peer-owner runs covered runtime profiles and refusals. C68
  archive and replay checks passed, including delayed watcher events.
  C82 passed schema and targeted rebuild tests with direct and shared
  peers.
  `$BB_THREAD_STORAGE/c68-runtime-profile-successor/proof.json`
  `$BB_THREAD_STORAGE/c68-test-imports/archive-socket-tests.log`
  `$BB_THREAD_STORAGE/c82-schema-names/combined-host.log`
  `$BB_THREAD_STORAGE/c82-projection-controls-host-verification.json`
- [AN-T-3921](../../ISSUES/AN-T-3921-CODE_SPEC_MISMATCH--resolve-the-workbench-atom-audit-contract-mismatch.md)
  records the open decision to restore or supersede AN-S-1948@3.
  Native admission confirmed the Issue. MCP was still syncing at the
  readback check.
  `$BB_THREAD_STORAGE/an-t-3919-audit-issue/native-readback.json`
- Four shared cold queries in reversed pair order took 16.444–18.708 s on
  `beta` and 13.033–17.198 s on `beta_next`. Most variation occurred
  before C71 was ready. The final performance gate remains pending.
  `$BB_THREAD_STORAGE/packaged-peer-owner-cold-abba/receipt.json`
- The first immutable image pair passed `query_run` through Web and MCP
  before and after a file edit.
  `$BB_THREAD_STORAGE/first-beta-pair-c61-T3Qy2EEc/query-comparison/packaged-query-results.json`
- The pinned Chromium 1248 build launched on the host as
  156.0.8078.4. Packaged browser tests use zero retries and retain
  failure traces. The read-only Docker preflight reached server 29.9.3
  with 15 images and 9.7 GB of builder cache.
  `$BB_THREAD_STORAGE/an-t-3919-packaged-verification/readiness.json`
  `$BB_THREAD_STORAGE/an-t-3919-packaged-verification/chromium-probe.log`
- The isolated `beta` and `beta_next` seals contain the same source
  except for the stack selector. Both carry five additional `.mjs`
  deletions and the Codex test TypeScript migration. The official C19
  strict source-language gate passed on the candidate delivery closure
  of 1,932 paths. The retained `beta` report found five C70 models.
  `$BB_THREAD_STORAGE/an-t-3919-final-progress/sealed-pair-replay.json`
  `$BB_THREAD_STORAGE/an-t-3919-sealed-92/corrected/source-pair.json`
  `$BB_THREAD_STORAGE/beta-language-assessment/final-92-corrected-beta-next-strict.json`
  `$BB_THREAD_STORAGE/beta-language-assessment/final-92-corrected-beta-report.json`
- A post-seal C82 test passed a real API restart against the same peers,
  kept the prior query available, and preserved Project binding refusal.
  The CLI diagnostic text differs from C70.
  `$BB_THREAD_STORAGE/c82-restart-draft/receipt.json`
- Scoped C82 tests verified startup replay, draining accepted calls,
  saved-SQL URL fallback, and shared initial abort and recovery. Three
  starts on one database covered initial load, reuse, offline edits,
  and archive catch-up.
  `$BB_THREAD_STORAGE/c82-replay-gate/code-access.json`
  `$BB_THREAD_STORAGE/c82-saved-sql-url-fallback/summary.json`
  `$BB_THREAD_STORAGE/c82-startup-checkpoint/successor-receipt.json`
  `$BB_THREAD_STORAGE/c82-initial-control/graph.json`
- An exact C70 retirement map records the files, registrations,
  surviving owners, and Spec bindings for the isolated rehearsal.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/cutover.md`
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/inventory.json`
- C21 AN-S-3044@62 routes real CLI and HTTP tests through their entry
  points. The scoped graph removed five CLI/HTTP denials and one shared
  gateway denial. Their focused tests passed.
  `$BB_THREAD_STORAGE/c21-cli-stdio-tests.log`
  `$BB_THREAD_STORAGE/c21-shared-health-tests.log`
  `$BB_THREAD_STORAGE/c21-tests-findings-shared-health-after.json`
- TTL settings coverage moved from C45 to the C71 startup owner under
  AN-S-3333@27. It preserves default, refusal, and expiry assertions.
  The move cleared one C45 denial.
  `$BB_THREAD_STORAGE/c45-ttl-3919/settings-migration.md`
- C45 cleared its remaining six denials. AN-S-3059@56 exposes the
  original operations only to its Test Package. All 68 focused tests
  passed.
  `$BB_THREAD_STORAGE/c45-test-surface-3919/code-access.json`
  `$BB_THREAD_STORAGE/c45-test-surface-3919/tests.log`
- The C53 Test Package now owns CLI admission coverage. The fixture was
  unchanged, and all eight focused tests passed.
  `$BB_THREAD_STORAGE/c53-admission-test-transfer/proof.json`
- Post-seal C21 factory checks passed in real direct and shared roles,
  including the expected query row on both stacks. All 36 import-order
  checks passed.
  `$BB_THREAD_STORAGE/c21-tests-findings-factories-after.json`
  `$BB_THREAD_STORAGE/c21-shared-module-proof.json`
- Both isolated 0.4.4.74 candidate images built. The `beta_next` image
  fingerprint matches its passed strict gate. The exact image IDs are in
  the receipts.
  `$BB_THREAD_STORAGE/an-t-3919-sealed-92/corrected/beta-build.json`
  `$BB_THREAD_STORAGE/an-t-3919-sealed-92/corrected/beta_next-build.json`
- All six packaged comparisons passed on these exact images. Both stacks
  matched fixture bytes, 33 Tool descriptors, query rows, and View
  lifecycle in direct, stdio, and shared modes. Production port bindings
  were unchanged.
  `$BB_THREAD_STORAGE/packaged-peer-owner-smoke-92/receipt.json`
- Both sealed images completed 650 lifecycle readbacks on identical
  fixtures. Each admitted 650 deltas with zero extra full generations.
  Beta Next had lower medians for all 13 operations. It exceeded 500 ms
  10 times versus 468 for retained Beta. Host load varied between runs,
  so the timing difference has no isolated cause.
  `$BB_THREAD_STORAGE/beta-lifecycle-benchmark-92-confirmation/comparison.json`
- The first retained Beta run stopped after 46 readbacks with an
  uncertain file effect. The same image completed a fresh fixture.
  The original failing file operation remains unknown.
  `$BB_THREAD_STORAGE/beta-lifecycle-benchmark-92/diagnosis.md`
- On the frozen current-sized Project, the guarded warm startup phase
  took a median 2.124 s for 6,063 foreground carriers. Reads and census
  took the most time. Atom loading and lifecycle take priority over
  standalone MCP and API startup.
  `$BB_THREAD_STORAGE/c69-startup-census/current-measurement.json`
- After the seal, the `beta_next` host HTTP path returned the expected
  query row. C16 tolerates a missing staging name after publication and
  still checks the carrier. C69 removed a duplicate folder hash pass
  and preserved backslash rejection. Focused source tests passed.
  `$BB_THREAD_STORAGE/host-beta-next-check.py`
  `$BB_THREAD_STORAGE/c16-staging-publication/focused.log`
  `$BB_THREAD_STORAGE/c69-startup-diff/tests.log`
- The live checkout selects `beta_next` and retains the `current` build.
  C70 authored source, active authority, and test registrations are retired.
  Exact predecessor Specs are archived. The running installations kept
  their existing image and port bindings.
- The fresh whole-Project graph checked 9,944 import occurrences with
  zero denials, undeclared bypasses, or production imports from Test
  Packages. Ownership, Lean, Structure, language, and 45/300 passed.
  The deliberate C74 fixture and declared bypasses remain.
  The sealed source passed all 36 C19 Static tests. Preexisting ignored
  bytecode caches blocked the in-place C19 prerequisite. The separate
  bytecode source and source-comment checks passed.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/post-cutover-whole-project/receipt.json`
- Image `sha256:6a1b40d58e3e3d7d66ecd52e30df5b7acc342c5adcaac2a61e00d2edd25ec953`
  passed 31 packaged tests and the full-Project MCP canary. A BB restart
  interrupted canary staging after E2E passed. The canary resumed on
  the same image and verified an MCP SQL readback.
  `$BB_THREAD_STORAGE/c70-cutover-rehearsal/final-workbench-seal.hpi0GkfK/resumed-canary-result.json`
- The packaged lifecycle benchmark completed 650 MCP-to-SQL readbacks
  with 650 native deltas and zero extra full generations. It observed
  362 samples above 500 ms and a 2,924.079 ms maximum.
- On Docker's bind mount, destination lookup failed after staging cleanup.
  C16 now verifies the destination first. Workbench background refresh
  keeps the selected View while it exists. The browser regression failed
  on the previous image and passed on the final image.

## Deferred

Multi-worktree support is deferred. Future work must keep the main checkout as
the default, discover registered same-parent `<repo-name>-<postfix>` worktrees,
and isolate whole-Project reads, writes, and refreshes across Specs, Tickets,
configuration, code and graph, runtime state, Web, and MCP. This does not gate
this Epic.
