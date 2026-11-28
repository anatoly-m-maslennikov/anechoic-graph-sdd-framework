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
  version: 38
  updated_at: "2026-11-27T23:39:23.375493+00:00"
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

### Public verdict proof and unobserved renderer guards

The pinned C90 command now reports `verdict_proof` separately from the
finding proof. Lean resolves the declared export and proves the
comparison policy for every modeled heap-backed list of strings.
A precedence mutation leaves the verdict unresolved and exits
nonzero. The report retains the proved finding effect and its three
matched bindings. Missing, empty, and wrong-type proof artifacts
also leave the verdict unresolved.

The pinned C87 command used to pass a Solution with an added return
guard that the shape replay never observed. The same Manifest,
Solution, renderer, and witness pins now report `solution_gap` and
exit nonzero. All four diagram calls still match. The valid
published pair still passes.

All 14 focused Functional tests passed with Autoform and Lean. The
C90 check covers the verdict policy and finding obligations. The C87
check covers the admitted shape workflow and calls. External effects
and other implementation paths remain unresolved.

For the fixed C88 witness, independently built strings match both the
fresh native capture and the buffered Lean observations. Changed
join, literal ordering, and string serialization sources fail pin
admission. General serialization, process effects, and the public
implementation comparator remain unresolved.

### Public Spec Comparison replay

C74 now compares the pinned C88 Manifest and Solution with fresh
implementation Lean on one mixed input. Lean checks the three ordered
directions against the authored effect and terminal path. The returned
report contains eight checked facts and the expected conflicting domain
verdict. The wrapper reports agreement on the witness.

The two fixed join observations replace only the exact unsupported
assignments. Lean executes the rest of the generated function. The
worker receives the exact reviewed bytes. The public replay rejects
changed source pins. The worker classification proof rejects a branch
swap. All three focused Functional tests pass.

General serialization, other inputs, Python consumer visibility,
and runtime effects remain unresolved.

C85's translated missing and empty boundary cases retain the source,
field, and message. Three checks pass on the pinned validator. All
three fail when the translated diagnostic loses its source argument.
Full parsing and validation effects remain unresolved.

### C89 client admission

Autoform translated the exact C89 sibling-delegation source against
Active AN-S-4936@1 and AN-S-5031@1. All three Lean probes reached the
unsupported `call:isinstance` boundary before the admission check.
C89 client admission remains unresolved.

### C90 verdict from authored Specs

The C90 public replay checks Active AN-S-4937@4 and AN-S-5024@4
against the translated shared export. Lean proves that the Manifest
Contract, Solution, and implementation choose one verdict for every
modeled heap-backed list of strings.

Two Functional controls pass. Lean rejects an agreeing change to both
Specs and a Solution guard that excludes a conflict-only list. The
finding formation proof passed in the same public replay. AN-S-3394@18
describes the authored Lean digest in the report.

### C75 workflow handoff and relative imports

Lean checks the pinned C75 Contract and Solution against the emitted
workflow body with supplied child results. The renderer model and
returned model match the normalizer result. The supplied ValueError
reaches the caller before rendering. A changed Python call that gives
the renderer the raw configuration fails the Model handoff check.

The combined Autoform translation bound missing child imports to C75's
root facade. C74 now stops before translation when this fallback would
bind a different staged module. It reports the importer and both paths.
The C87, C88, and C90 comparison groups pass import admission.

The native public check confirms the C75 export and child bindings.
The Lean replay uses the translated leaf and explicit read-only probes.
Full Autoform initialization and child implementations remain unresolved.

### C84 compact Lean strings

A zero-width joiner in a normalized effect value caused the old encoder
to expand every scalar into a Lean character constructor. Lean failed
to elaborate the 16,384-scalar example at its recursion limit.

The encoder now emits quoted Lean strings. Lean 4.31 decoded the exact
effect value without changing its limits. The generated file shrank
from 264,428 bytes to 17,310 bytes. C84 round-trip checks cover control
characters, literal escape spellings, Unicode, and surrogate rejection.

The C88 comparison passed with the new encoder pin. Fresh Autoform
execution of the encoder stops at string join or hexadecimal formatting.
Translated encoder execution remains unresolved.

### Bounded C88 JSON and worker replay

Fresh translation of the seven pinned implementation files used an
isolated Autoform model for the exact JSON options in the worker. Four
inputs produced the same bytes as Python and matched 23 independent
comparison facts in Lean. The cases cover nested values, Unicode,
escaping, missing values, and Boolean, null, and integer distinctions.
The model refuses different JSON options. It excludes floats and other
unsupported values.

The translated public entry advanced to the Python default argument
boundary. General JSON, public invocation, and runtime process effects
remain unresolved.

### C88 public reports with a guarded runner

The translated public entry produced four reports with all 23 facts and
three direction names in the expected order. Independent typed
expectations matched each report. Corrupted expectations conflicted.
Changed worker bytes and an unexpected Lean executable stayed
unsupported.

The replay used the bounded JSON model and supplied actual Lean worker
outputs only when the program bytes and executable matched. The
translated comparison and report bodies ran without substitutions.
Direct execution through the Python runner, other inputs, and external
process behavior remain unresolved.

The live Python entry also returned those four reports through the real
Lean subprocess. The runner rejected invalid JSON and a nonzero Lean
exit. The Autoform replay still supplies the process result at its
explicit boundary.

## Current C89 and C95 verification

For the pinned C86-to-C84 call, C89 admitted the declared sibling and
refused the wrong parent and missing client interface. Six cases passed
through the translated admission predicate. Lean rejected a control that
ignored the interface. Other delegated arguments and exact return values
remain unresolved.

C95 returned the same exact carrier digests in staged and offline reads
with AN-S-5021@3 and AN-S-5023@2. Both modes refused the stale Manifest
revision. Lean matched the captured snapshot ID, rejected an empty ID,
and reported an unobserved ID as unresolved. This uses an in-process
DuckDB route. Full translated source loading remains unresolved.

## Current C89 module and C84 literal replay

The full pinned C89 module emitted under Python 3.14 and passed all
six admission cases in Lean. The interface mutation changed only the
wrong-interface result. The exporter omitted signature metadata under
Python 3.15 because the generator scope name changed. Other C89
implementation paths remain unresolved.

The pinned C84 encoder matched Python on seven inputs with a bounded
join model. Lean rejected a changed opening quote and parsed the
original Python output for nine inputs. The two translated control
cases still require the hexadecimal formatting model.

## Current workflow and diagnostic checks

The C75 workflow test now selects AN-S-5022@9 and displays admission
diagnostics before checking the source receipt. All six workflow tests
passed. The translated check rejected the renderer receiving the raw
configuration. The registered C89 full-source admission test also passed.

C90's fresh verdict and finding proofs exceeded the 120-second guard.
The prior proved Python source and public export have the same ASTs as
the current files. The formal source digests agree, and 341 native
verdict cases passed. The fresh proofs remain unresolved.

The scratch C84 hexadecimal model failed to compile in Autoform Stdlib.
The native round-trip checks passed, and the two translated control
cases remain unsupported.

## Bounded C84 control-character replay

The C84 encoder passed all nine cases with a scratch-only formatter and
join model. The formatter matched Python across all 256 byte values
and refused other values or format specifiers. Lean rejected a change
to the C1 upper boundary. The emitted encoder body was preserved apart
from a redirect of the exact formatter call. Native Autoform still
leaves that call unsupported.

## Current C90 Lean proof

The serial verifier proved the current finding and verdict obligations.
It left the precedence mutation unresolved. Both runs used the normal
120-second proof deadline and the current source pins. This resolves
the earlier timeout for these obligations. Other C90 coverage remains
as recorded above.

## Current C87 renderer replay

Both pinned public renderer tests passed. The verifier detected a stale
implementation pin and a dispatcher that dropped its diagram. It left a
different diagram unresolved. A Solution requiring an unobserved output
field withheld a passing result even when the observed call forms
matched. These tests cover the selected shape cases.

## Current C83, C88 and C92 replay

Autoform Lean accepted the exact C83 link to AN-S-4930@2 and refused
the stale link to @1. Removing the version check from the Python
source made the translated negative control fail. C83 preserved
the refused Solution source and relation field in native staged
execution. Lean exposed the exception type only.

C88's public comparison matched the pinned mixed witness across
all three directions and refused a stale implementation digest.

C92 generated 134 cases from the pinned C30 framing Specs. Lean
agreed with both role results for every case. A one-byte slice
mutation in C92 changed 40 cases, and Lean rejected the output.
Direct Autoform execution remains unresolved at map.

The selected C75 Functional modules ran 140 tests with three
skips and no failed modules. The optional C88 replay passed
separately. The full implementation comparison remains open.

## Frozen implementation replay

The scoped Engine Studio snapshot passed the C75, C87, C88, and C89
implementation replay cases. C90 passed the shared verdict policy
case and rejected a wrong diagnostic message. The reordered diagnostic
case proved all finding values but left the verdict proof unresolved
after 120 seconds. Six of seven selected tests passed. All pinned
candidate digests matched after the run.

Keep full implementation comparison open. This replay covers the
selected witnesses and mutations. The C90 result does not establish
verdict conformance for the reordered diagnostic case.

## Current C85 normalization replay

The current translated C85 normalizer matched three witnesses with
Active AN-S-4932@2 and AN-S-5026@3. Lean rejected changing the Solution
finding's source to the Manifest source. The replay uses captured
Python parser and validator outputs and a verified prior translation
of the diagnostic function. Full translated execution of those
dependencies and external effects remains unresolved.

## C90 reordered diagnostic replay

The instrumented replay proved both the diagnostic values and the
public verdict for the exact reordered implementation that timed out.
The Manifest, Solution, authored Lean and verdict proof digests match
the prior result. The proof deadline was 120 seconds in both runs.
The full frozen run still records its original timeout.

## C85 authored comparison

The public formal verifier compiled AN-S-4932@2 and AN-S-5026@3.
A bounded Lean check related the translated nominal return to the
authored normalization effect and output. Lean rejected changing
the Contract's model binding or the Solution's terminal output.

The check maps a normalized return to the declared effect. Runtime
event emission, ordering, full translated dependencies, and Code
Access context remain unresolved.

## Current C88 implementation pin

The width change to the C88 comparison source required a new
implementation digest. The public verifier and test request now
use that digest. All three C88 tests passed. The translated mixed
witness matched, the changed source was refused, and Lean rejected
the swapped worker classifications.

## C89 sibling admission and C95 pin validation

Both C89 public checks matched a pair whose pinned parent headers
contained only whitespace. The C89 Contract requires a nonempty
common parent. C95 now refuses blank source identity strings before
loading the carriers. The exact-pin regression failed on both calls
before the fix and passed after it. Twenty-two native tests passed,
including the original valid sibling control.

The exact translated C89 predicate accepted an omitted transport for
an in-process call and refused it for HTTP. The interface mutation
still failed its comparison. This check covers the admission predicate.
Full translated C95 loading and C89 orchestration remain unresolved.
