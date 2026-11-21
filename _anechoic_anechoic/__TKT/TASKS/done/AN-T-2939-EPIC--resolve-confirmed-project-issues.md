---
atom_family: TKT
atom_id: AN-T-2939
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
  label: Epic
relations:
  REFERENCES:
  - AN-T-1034
  - AN-T-1035
  - AN-T-1037
  - AN-T-1671
  - AN-T-2029
  - AN-T-2035
  - AN-T-2036
  - AN-T-2037
  - AN-T-2038
  - AN-T-2039
  - AN-T-2040
  - AN-T-2041
  - AN-T-2042
  - AN-T-2043
  - AN-T-2044
  - AN-T-2045
  - AN-T-2046
  - AN-T-2047
  - AN-T-2048
  - AN-T-2049
  - AN-T-2050
  - AN-T-2051
  - AN-T-2052
  - AN-T-2053
  - AN-T-2056
  - AN-T-2057
  - AN-T-2062
  - AN-T-2063
  - AN-T-2064
  - AN-T-2066
  - AN-T-2067
  - AN-T-2069
  - AN-T-2225
  - AN-T-2227
  - AN-T-2229
  - AN-T-2480
  - AN-T-2485
  - AN-T-2486
  - AN-T-2755
  - AN-T-2756
  - AN-T-2781
  - AN-T-2783
  - AN-T-2784
  - AN-T-2785
  - AN-T-2786
  - AN-T-2787
  - AN-T-2788
  - AN-T-2789
  - AN-T-2790
  - AN-T-2799
  - AN-T-2933
  - AN-T-2936
  - AN-T-2937
state:
  status: "done"
  version: 1
  updated_at: "2026-11-21T00:58:05.205946+00:00"
---
## Summary

Resolve confirmed Project Issues

## Objective

Review every active and Backlog Issue against the current Code and Specs. Fix and verify confirmed defects. Leave uncertain Issues open.

## Work

- Check the 53 Issues in the starting inventory.
- Fix confirmed defects and verify their normal entry points.
- Record every outcome and resolve Issues with verified evidence.

## Definition of Done

Every Issue in the starting inventory has a disposition. Verified fixes have evidence. Uncertain Issues remain open with a recorded reason.

## Results

Reviewed 53 Issues. Resolved 24 and left 29 open. Six fixes landed in this checkout. Closed-descendant preservation is a partial fix for AN-T-2937.

Checks passed for native MCP and graph behavior, source discovery and launchers, and Local Release. Playwright discovered all 34 Workbench cases.

| Issue | Outcome | Evidence |
| --- | --- | --- |
| AN-T-1034 | Open | Codex host rendering still needs a live host check. |
| AN-T-1035 | Open | The historical Source Synopsis Issue has no verified Current successor. |
| AN-T-1037 | Fixed | Role discovery stops at the carrier marker. Filename regressions passed. |
| AN-T-1671 | Verified | Discovery accepts a positive Work Sequence prefix. |
| AN-T-2029 | Open | Native Draft promotion preserves Epic children. The one-call Update contract is still open. |
| AN-T-2035 | Open | Legacy cascades and native guarded Status moves differ. Current scope is unclear. |
| AN-T-2036 | Open | The old replacement failure has no confirmed native reproduction. |
| AN-T-2037 | Open | Host Skill refresh still selects predecessor assets. The intended cutover path is unclear. |
| AN-T-2038 | Verified | Compatibility reread retains loaded Archive coverage. |
| AN-T-2039 | Verified | A failing live Query and the Query Store test returned errors without SQL or literals. |
| AN-T-2040 | Verified | The native provider returns a Status result for a single target. |
| AN-T-2041 | Open | Schema rejection can still preempt per-field corrections. |
| AN-T-2042 | Verified | Embedded density no longer changes the standalone Workspace binding. |
| AN-T-2043 | Open | Release SHA evidence exists. A parented Step and Action Run are missing. |
| AN-T-2044 | Fixed | MCP bootstrap stages atomic replacements under Project temporary storage. Failure preserves the destination. |
| AN-T-2045 | Open | The active formal-block Specs differ on the required fence. |
| AN-T-2046 | Verified | Tests confirm that legacy pending corrections are session-scoped. |
| AN-T-2047 | Verified | Compatibility refresh uses targeted audit and inventory updates. Native coverage is AN-T-2485. |
| AN-T-2048 | Open | The HTTP Archive alias works. Native Archive load behavior still needs a decision. |
| AN-T-2049 | Verified | SQL edits and Check requests clear the previous verdict. |
| AN-T-2050 | Verified | Storage errors emit a warning and let standalone Workbench start. |
| AN-T-2051 | Verified | The launcher validates the built image fingerprint again before startup. |
| AN-T-2052 | Verified | The direct Docker build and outer launcher have finite timeouts. |
| AN-T-2053 | Open | Readers still differ from the shared validated snapshot. The integration boundary is unclear. |
| AN-T-2056 | Verified | Saved Query results include a configured public URL or an explicit reason it is unavailable. |
| AN-T-2057 | Fixed | Local Release locks before shared mutations and verifies installed Framework and Skill files. |
| AN-T-2062 | Open | Independent native copies need a decision on identity and placement. |
| AN-T-2063 | Superseded | The Current MCP Spec publishes Tool help through tools/list. |
| AN-T-2064 | Open | Query-bound selection rejects ambiguity. Legacy fallback can still read multiple carriers. |
| AN-T-2066 | Open | The active Specs differ on how to serialize source provenance. |
| AN-T-2067 | Open | Host Entity Graph still reads the filesystem. The replacement bindings are unverified. |
| AN-T-2069 | Verified | Local Release packages the checkout tree, including the frontend manifest. |
| AN-T-2225 | Verified | Native Workbench publishes implementation_rmedo and import_nodes. |
| AN-T-2227 | Fixed | Sidecar-only refresh updates affected Package pins and audit rows in one transaction. |
| AN-T-2229 | Open | The owner rule exists. The pilot trace cluster assignment is unverified. |
| AN-T-2480 | Verified | Focused tests cover Container placement and Plan/Plan audits. |
| AN-T-2485 | Open | Ordinary native refresh still captures all Atom sources. A safe delta path is unverified. |
| AN-T-2486 | Fixed | Moved the standalone migration scenarios to their own test file. Playwright discovers all 34 cases. |
| AN-T-2755 | Open | The shared Ticket Run ID is deferred. |
| AN-T-2756 | Open | The sibling dependency direction is still undecided. |
| AN-T-2781 | Open | The full Summary slug rule conflicts with filename length limits for these carriers. |
| AN-T-2783 | Open | Four Steps lack the specified parent. Moving them also affects native Workflow pin paths. |
| AN-T-2784 | Answered | The Operator approved using the title when an Archive Summary is empty. |
| AN-T-2785 | Open | Archive-only bare references still need a visibility decision. |
| AN-T-2786 | Open | Native lifecycle tests passed. The specific PMETA Workflow remains unverified. |
| AN-T-2787 | Open | The authority for the disputed CA-O-098@1 history is unverified. |
| AN-T-2788 | Open | The current Archive differs from the earlier preservation receipt. |
| AN-T-2789 | Open | The shared Action history mapping and placement remain unverified. |
| AN-T-2790 | Open | Current and Backlog decisions exist. Archive reconciliation is deferred. |
| AN-T-2799 | Open | CA-C-453 has a disposition. Other lineages remain open. |
| AN-T-2933 | Verified | The editor waits for CodeMirror readiness. The isolated release browser check passed. |
| AN-T-2936 | Fixed | Native MCP creates and promotes Epic and Sub-epic Drafts. The registry advertises both. |
| AN-T-2937 | Open | Status changes now preserve closed descendants. Canceling unfinished descendants remains open. |
