---
atom_family: TKT
atom_id: AN-T-3485
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 17
  updated_at: '2026-11-27T10:19:58.444018+00:00'
---
## Summary

Generate and compare Studio implementation Lean

## Work

Use Spec Engine and its child Components for the current implementation
verification. Generate Lean evidence from their actual code independently
of the authored Manifest and Solution. Compare both in Lean with exact
source pins, and report unresolved obligations.

Use one additional Component example when it exposes a gap in the eDSL
or verifier. Edit a Spec Engine carrier when it resolves a confirmed
mismatch or proves a fix.

## Findings

Fourteen Lean blocks and 21 workflow declarations compile. A Lean 4.19 compatibility shim works in scratch. Full conformance remains unsupported. Retain unresolved cases and do not close this comparison.

The Lean 4.31.0 baseline checked C75 and all eight children. The full
Spec Engine suite passed 244 tests and 296 subtests. Targeted comparison
found missing mixed-profile coverage, ordering mismatches, lost C85
provenance, an undocumented C86 status, and a C89 rejection mismatch.

### Follow-up implementation verification

C87's exact translated shape renderer passed four Lean cases using the
published Atom shape. Lean rejected a field substitution. C88's exact
translated entry passed the three ordered comparisons to its worker.
Lean rejected a missing comparison.

C86 rejects malformed bounds and body values from Lean. The exact
translated predicate passed nine Lean cases and rejected a mutation
that accepted byte 256. The published Contract's witness array matched
133 observed inputs in one C30 framing comparison.

C95 now requires the same Project-relative pins for files and ingested
snapshots. Both verifier modes reported the same exact Active sources
and rejected an absolute Manifest pin.

Other renderer profiles, full translated C86, C88, and C95 execution,
and external effects remain unresolved.

### Pinned implementation comparisons

The C74 command accepts exact Manifest, Solution and implementation
SHA-256 pins. The C30 framing check matched 133 current witnesses and
found six distinct bounds mismatches in the historical CRLF
implementation. A stale pin stopped comparison.

The C90 check used Active AN-S-4937@2 and AN-S-5024@2. Autoform-translated
Lean matched the three declared value equalities on one input. A
wrong-field implementation and a changed Contract each gave a
conflict. An unchecked return branch leaves the Solution facts
unresolved.

The trace verifier requires a reachable explicit output before it
reports matching outcome obligations. Lean string emission rejects
unpaired surrogates. Regression controls cover both defects.

Further Studio implementation behavior and unobserved effects require
evidence. The C90 witness does not cover the separate verdict operation.

### Tool API branch coverage

C88 requires evidence from every provider dispatch branch to confirm a
precondition. The public verifier reports a match when both branches
agree, unresolved when evidence is missing, and a conflict when an
observation contradicts the Contract.

Lean evaluated five branch-merge cases from the exact translated C88
source. A mutation that accepted partial evidence failed the missing
branch case. All 36 focused functional tests passed. The full translated
Tool API projection remains unresolved at the unsupported set call.

### HTTP comparison coverage

C88 lists declared HTTP request and response schemas as unresolved when
the workflow does not check schema conformance. A partial response
observation keeps a known status or envelope contradiction visible.

Lean compared the exact translated response projection with a pinned
authored HTTP outcome on six cases. The incomplete-pair mutation failed
both contradiction cases. All 34 focused functional tests passed.

### Pinned renderer comparison and Query evidence

The C74 command can compare C87 with pinned C87 and C52 Specs and two
implementation digests. Both configured shape field orders pass. The
command rejects stale bytes and detects the mutation that drops the
diagram. A different valid layout remains unresolved.

C88 requires a C59 Run observation with full submitted SQL and selected
Project evidence before confirming the complete-query guarantee.
A partial observation remains unresolved. A known contradiction is
reported. The current evidence checks the declarations and comparator.

### C90 finding preservation

The pinned public C90 command checks a witness and proves that the
translated finding preserves the three authored values for all inputs,
heaps, and globals addresses. Reordered dictionary fields still satisfy
the proof. A mutation that changes the message only on an untested
input passes the old witness but cannot satisfy the proof. Lean also
confirms the concrete counterexample. Verdict remains unresolved.

### Lean result admission

C84 rejects bare non-JSON numeric constants. Six real Lean executions
match the published success and failure cases. The exact translated
constant handler raises ValueError for NaN and both infinities. Full
runner translation remains unresolved at unsupported Python defaults.

C86 checks each bounded framing observation against its own role's
expected witness result. The public verifier rejects a wrong body and
a copied role that hides a mismatch. Five translated guard cases pass.
The pinned C30 comparison still passes 133 cases. Full validator
translation and unbounded framing equivalence remain unresolved.

### Diagram admission and C30 framing proof

C94 requires a nonblank Mermaid diagram before comparison. A missing
selected Solution Action reports its exact source pin. Whole-chain CLI
verification still reports a renamed Action as a conflict. The Active
C94 pair passed one valid replay and four source-linked failure cases.

The exact translated guard rejects a missing diagram. Autoform cannot
execute the full coordinator or the positive string-strip path.

Lean proves C30 bounds and body equivalence for every input and path
across the pinned Drafts and the AST-linked implementation model.
The Functional test checks the proof against the public verifier output.
A mutated Solution passed all 133 samples, but Lean found an input
where it disagreed. CPython regex execution and path conversion remain
outside that proof.

### Public proofs and staged Structure pins

The C30 command now runs the universal proof and reports it separately
from the 133 sample cases. A failed proof stays unresolved and retains
the bounded observations. The proof covers the generated models.

C87 and C90 check that the selected Manifest export binds to the
translated implementation. The report records the observed shared
module digest. A missing binding and a redirected export stay
unresolved. The redirected control reports its actual target.

C93 now compares each selected carrier digest at request, snapshot
creation, and return. AN-S-5018@6 and AN-S-5019@4 are Active. C75's
updated delegation resolves to AN-S-5018@6. Ten replays check changed,
omitted, or unobserved pins. Lean proves that both translated digest
assignments preserve any digest in the modeled heap. Full staged
execution remains unresolved at unsupported Python defaults.

### Export replay and diagnostic formation

C87 and C90 replay the selected shared module against a supplied
export SHA-256. Changed bytes stop the replay before witness execution.
Both Lean witnesses invoke the function read from the translated
shared module. A native check confirmed both bindings through the
trusted C75 consumer in this checkout.

The public C90 proof establishes diagnostic formation and preserves
all three input values. A conflicting Solution effect is reported as
a mismatch. A formation effect or additional guard outside the
observed path stays unresolved even when all three values match.
A pinned Solution with a fourth return guard reproduced the false
success before the fix. C30's pinned proof still passes.

Python importability for supplied Projects, additional C90 effects,
and full implementation translation remain unresolved.

### Pinned framing verdict and Autoform metadata

The pinned C30 command keeps all 133 sample results when Lean cannot
complete the universal proof. It reports unresolved and exits nonzero.
An extra prefix in the generated model passed every sample and failed
the proof. The admitted framing model still passes samples and proof.
The verifier now requires all four typed bounds and body statements.
Removing the Manifest body theorem preserves the samples and leaves
the proof unresolved.

Autoform now uses the Python interpreter that runs the Engine command
unless the caller supplies an explicit override. The same upstream
metadata pass failed on 70 of 105 Spec Engine sources with PATH Python
3.15.2. Engine Python 3.14.7 processed all 105 and recovered 488
additional function signatures.

An exact replay of the C84 string encoder now reaches its
`str.isprintable` call. Autoform cannot evaluate that call, so the
encoder comparison remains unresolved.

The selected C87 shape renders through its translated public export.
The full framing path stops at C85's module initialization, and the
workflow path stops at `enumerate`. Replacing the framing generators
with explicit loops does not resolve the remaining operations.

The golden corpus and the pinned C30, C87 and C90 regression checks
passed. Unsupported Python operations and unmeasured obligations remain
unresolved.

### C88 valid comparison replay

The Functional check now reads the exact Active AN-S-4935@1 and
AN-S-5030@1 pair. It checks that the public report keeps its source
pins and returns all three declared directions.

The translated C88 entry returned the complete report for one
mixed-input replay. The translated program return reproduced the
actual Lean worker byte for byte. Lean checked the worker's result
count, order, and classification. Swapping the matched and conflicting
outcomes failed both classification proofs.

The replay observes two joined strings in Python. It checks the worker
bytes and Lean executable before admitting the actual output. A change
at either input is rejected. Missing obligations raise `ValueError`.
Unbridged Autoform execution still stops at the generator expression.

### Independent report and snapshot receipt checks

The C88 replay now checks the complete report against independent
expected facts. It also checks both published carrier digests and the
generated Model digest before replay. The Functional test binds the
Active pair by digest and checks each fact's values and verdict.

The C71 DuckDB route, C69 staging, C95 pinned reads, and C75 admission
preserve the same nonempty snapshot ID. Lean matches the observed ID
against the Active Contract and rejects an empty ID. An unobserved ID
stays unresolved. The replay uses in-process HTTP transport and stops
at Model Generator delegation.

### Unchecked obligations and blank results

A C90 replay returned success after the Contract added an integer
requirement for the returned message. The verifier had not checked that
type. It now reports the exact unmeasured obligation and keeps the
proved bindings and formation. The command exits nonzero. A checked
conflict still makes the verdict a mismatch.

C87 now treats whitespace-only output as an absent diagram. Both field
orders report a mismatch. The Unicode whitespace case agrees with the
Spec Engine's existing renderer admission. A different nonblank diagram
layout stays unresolved.

An explicit-loop C88 experiment emitted identical Lean for four native
cases. Autoform reached unsupported JSON serialization on the mixed
input. The staged valid replay still provides evidence at those
boundaries.

### Renderer call forms and snapshot IDs

C74 reproduced a false pass with the pinned C87 and C52 Specs. A
renderer with a renamed keyword still produced the diagram when called
without keywords, but the real C75 call raised `TypeError`. The
translated replay now checks both call forms for each field order. Its
report shows which call conflicts. The same mutation exits nonzero and
the unchanged renderer passes.

The Lean trace value check used ASCII trim for `nonempty_string`.
Whitespace-only Unicode and control strings could pass. The Lean
predicate now agrees with Python whitespace classification across all
Unicode code points. A staged C75 admission also accepted such an ID
before the fix. C75 rejects blank IDs before invoking the Model
delegate. The pinned C95 replay still carries one valid snapshot ID
from the DuckDB route through Worker staging to C75. Lean rejects the
blank observation. Unobserved IDs and malformed event rows stay
unresolved.

### Unbounded verdict comparison

The published C90 Manifest declares the shared verdict export. Lean
resolved that export in the freshly translated facade and provider.
For every modeled list of strings, a conflict wins. An empty list or
an unresolved entry without a conflict yields unresolved. Other lists
yield matched. The reference uses the comparison policy for conflict
precedence and the existing verdict controls for empty input. The
published Contract specifies the separate finding operation.

The same proof rejected a Python mutation that gave unresolved
priority over conflicting. The two mixed orders failed in the boxed
list replay, and all six boxed controls passed on the original.
The Functional regression now regenerates the implementation Lean.
The universal theorem covers heap-backed lists in Autoform.
