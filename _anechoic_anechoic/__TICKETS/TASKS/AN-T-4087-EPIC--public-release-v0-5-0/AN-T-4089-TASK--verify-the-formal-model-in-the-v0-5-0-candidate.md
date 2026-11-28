---
atom_family: TKT
atom_id: AN-T-4089
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Verify the formal Model in the v0.5.0 candidate

## Work

Confirm the Model Generator owner. Use AN-T-4062, AN-T-3488, and
AN-T-3489 to verify the shipped Model from its admitted inventory
through Lean validation, generation, and packaged Python loading.

### Code against Formal Specs

Compare the shipped code with the exact bound Formal Contracts and
Solutions. Replay supported success and refusal paths through the
implementation. Record unresolved or unsupported claims.

### Tests against Formal Specs

Map the tests and their assertions to the same formal obligations.
Generate and run cases where the generator supports them. Record
obligations with missing, stale, or insufficient test coverage.

## Review findings

Candidate `28d67aacfaeebb5552590de5de659167b78c3b8f` has open findings.

- C27, C45, C63, and C64 Solutions answer archived Contracts. Their
  current Manifest and Solution chains need a supported formal pairing.
- C30's carrier framing replay selects a Draft Solution that answers an
  earlier Draft Manifest. The Active Manifest lacks the framing action.
- C46 accepted a page for a different query ID. A successful bookmark also
  hid the result error. Focused paging checks pass. Verify both paths in
  the packaged browser suite.
- C46 accepted malformed Tool REST envelopes. Focused tests now verify
  exact envelope and Project receipt checks and preserve typed faults.
- C21 MCP accepted a Backend envelope with both a result and an error.
  The host regression checks that MCP and REST both refuse it.
- The C46 browser suite now collects after the test loader fix. Run the
  generated cases on the new sealed candidate.
- C21 generated document cases use Draft pins. Verify the Active Tool
  REST contract with coverage tied to its own pins.
- C45 returned HTTP 400 for a valid request whose result could not be
  serialized. The regression checks a sanitized HTTP 500 and preserves
  HTTP 400 for SQL refusal. Include the correction in the next seal.

The replacement C27, C45, C63, and C64 Solutions use Tier 0 and answer
their exact Manifest Drafts. Review the Drafts before promotion. Check
the trace obligations against the code and tests on the final seal.
Lean translation checks establish the chain shape and modeled facts.
The qualification probe passed 25 CLI and source preparation tests.
They cover dispatch, argument refusal, interruption, and scoped checkout
preparation. The Local Release installation and continuation evidence
remains part of the candidate gates.

The `c406b2b40a32d0e89f713274e0b415519e45bb06` probe generated a
Model from its packaged sources. The Lean-verified host run and the
same image produced equal Model and descriptor hashes and equal hashes
for all 94 generated Python modules. Both loaded the attested modules
and refused a wrong descriptor digest. The receipt records the image ID
and packaged source hashes. The final seal still needs the Project Model
handoff, negative cases, and the required release-gate evidence.

Twenty-four focused Model tests passed on the probe. They include source
selection and rejection, incompatible and tampered assets, and a
source-linked Lean rejection for an unknown Relation endpoint.

On `b597aa0eac2d50cf01b93d6c126f14e384556fb4`, Lean validated the
Project Model and Python loaded all 95 attested modules. Loading
refused a wrong descriptor digest. The image comparison remains open
for this seal.

The same probe matched all four proposed Active pair translations.
C27, C63, and C64 matched the modeled Manifest-to-Solution claims.
C45 matched operation, protocol, and input fields. Transport and error
fields and workflow-to-HTTP semantics remain unresolved. Four focused
HTTP callback and Project session tests passed, including the status
and response kinds of the tool API.

C21's Active REST pair is AN-S-3044@75 and AN-S-5186@5. It loads and
translates. The updated case driver generates all ten REST cases,
including `transport_refused` and `legacy_refused`. The refusal cases
have no input fixture in the claim. The test matrix maps all ten cases
to the C21 gateway tests. Those tests record the private calls and
replies, including unchanged Tool names and refusal before dispatch.
The generator and tests are in seal `0bcec465e0c153575d1e3d6b39482aef1d59e908`.
The separate MCP forwarding Decision still answers archived AN-S-3191@5.

The next isolated C21 proposal pairs Manifest AN-S-3044@76 with
Solutions AN-S-3366@8 and AN-S-5186@6. Pinned Lean matched the modeled
MCP action. All six case-driver tests passed and the ten generated
REST cases kept their values. The C21 gateway tests supply the refusal
requests. Manifest Code Access fields are unchanged. State, I/O, and
legacy REST value comparisons retain the recorded coverage limits.

The existing generator also emitted both MCP outcomes from the new
pins. A focused gateway replay checked the exact Tool invocation and
session forwarding, malformed reply failure after dispatch, and invalid
caller context refusal before dispatch. It used a mock private Backend.

The C30 proposal adds the framing operations as AN-S-3069@72,
preserves the shared @71 Code Access fields, and retains the earlier
Lean formulation. Solution AN-S-4742@4 and the C30 implementation
binding select @72. All 22 focused generated, comparison, and runtime
effect tests passed with pinned Lean. The direct comparison matched
133 cases. CPython regex execution and path conversion remain outside
that comparison.

The qualification seal updates the C46, C81, and CS1 implementation
bindings to their Active carriers. All 15 pins reviewed in the release
Packages resolve to one exact Active revision.

On `a99d4b49`, pinned Lean validated the Project Model. Python loaded
95 attested modules and rejected a wrong descriptor digest. The
corrected seal `cd3c911537` reproduced the same fingerprint, module
hashes, and refusal. The packaged Model comparison remains open.

On the same seal, 23 focused Model checks and the Functional Lean
relation-endpoint rejection passed. The checks cover duplicate and invalid
declarations, changed sources, missing bindings, and last-good fallback.

Six exact Manifest and Solution comparisons translated with pinned Lean
on `a99d4b49`. The release CLI and MCP forwarding comparisons match their
modeled directions. C45 HTTP fields and the C21 legacy value checks retain
coverage limits. Five focused C45 formal and Tool status tests passed.

The corrected seal keeps the 15 reviewed Active pins. Its 27 launcher
checks cover the Project lock and readiness boundary in AN-S-3044@76,
including one startup for concurrent requests.

The generated query contract drift check passed. Project Model generation
for TypeScript remains the separate AN-T-3490 follow-up.

## Acceptance

Record one fingerprint across the stages and the exact candidate
image. Confirm missing, ambiguous, invalid, and unbound Model inputs
fail before publication with source-linked errors.

Verify compile, reuse, and fallback with the matching Structure. A
refusal preserves the last accepted Model.

Record exact Spec pins, implementation findings, and test evidence.
Resolve mismatches and account for coverage gaps before release.

Retain the formal and Functional gates. Record the AN-T-3485 coverage
limits and the disposition of AN-T-3490. Obtain Operator approval
before deferring any existing Local Release requirement.
