---
atom_family: SPEC
atom_id: AN-S-3394
container:
  component: C73
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 17
  updated_at: '2026-11-27T11:28:38.692545+00:00'
---
## Summary

Declare Implementation Verification

## Purpose

Derive bounded Lean models from authored implementation and Realization Graph facts, including code units, calls, conditions, and effects. Keep source references and report unresolved coverage. Compare with the Lean model supplied by Spec Engine when a matching Spec exists.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C74',
    name='Implementation Verification',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['WORKERS_beta_C69__shared.python_code_units',
                               'ADAPTERS_C30__shared.frontmatter_bounds',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.parse_carrier',
                               'ADAPTERS_C30__shared.parse_component_manifest',
                               'ADAPTERS_C30__shared.formal_claim_fences',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.verify_formal_chain',
                               'carrier_compare.compare',
                               'carrier_model._SOURCE',
                               'carrier_model.generate',
                               'carrier_runtime_effects',
                               'carrier_formal._PATHS',
                               'carrier_formal.formal_inputs']},
          'exports': {'carrier_compare.compare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_model._SOURCE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_model.generate': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_runtime_effects': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_formal._PATHS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_formal.formal_inputs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']}}},
 'state': {'reads': ['source pin request, pinned implementation and formal inputs'],
           'writes': ['temporary Lean comparison file']},
 'io': {'server': {'carrier_compare': {'transport': 'cli',
                                       'runner': 'managed_python',
                                       'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
                                       'arguments': ['--root '
                                                     '<project-root>',
                                                     '[--lean '
                                                     '<executable>]',
                                                     '[--pins <source-pin-request.json>]',
                                                     '[--component C30|C87|C88|C90]']}}}}
```

## Component Contract

### Compare pinned implementation evidence

#### Guarantee

Derive Lean from the pinned Python source and compare carrier bounds and body with the pinned Manifest Contract and Solution. Return source pins, checked cases, mismatches, and unresolved coverage in JSON.

With `--pins`, supply a JSON object with `manifest`, `solution`, and `implementation_sha256`. Each Spec pin supplies `path`, `atom_id`, `version`, `status`, `container_component`, and `sha256`. Paths in Spec pins are relative to the Project. The default C30 check covers the admitted framing operations and their witnesses.

When the witnesses agree, Lean also checks the universal framing proof
against the two Specs and the source-derived model. The report gives
the proof verdict and its digest separately from the finite cases.
The proof must establish the bounds and body equations for both roles.
If Lean cannot complete the proof, the comparison remains unresolved.
The command retains the finite cases and exits nonzero.
CPython regex execution and path conversion require separate evidence.

For C87 and C90, supply `export_sha256` to require the same shared
module on replay. When it is omitted, the verifier checks and reports
the digest observed in that run. A changed digest leaves the replay
unresolved. Invoke the selected function through the translated shared
module. The binding must match the pinned Manifest and implementation.
Python module initialization and consumer visibility require separate
evidence.

With `--component C90 --pins`, compare the three declared finding
bindings and the declared formation of the diagnostic. Run a string
witness. Lean proves that the implementation forms the returned
diagnostic and preserves the three input values for every modeled
heap, globals address, and set of input values. Keep the witness
results if a proof remains unresolved. A checked formation conflict
makes the comparison a mismatch. An unmeasured formation effect
leaves it unresolved. Report every unmeasured obligation of the selected
finding under `unresolved_obligations`. Retain the checked results and
leave the comparison unresolved unless a checked obligation conflicts.
Prove the shared verdict policy for heap-backed lists of strings.
Report its theorem and proof digest under `verdict_proof`. If the
verdict proof fails, keep checked findings and leave the result
unresolved unless a checked obligation conflicts.

With `--component C87 --pins`, the request pins the C87 Manifest and
Solution and a C52 shape pair under `witness`. The witness supplies
`manifest` and `solution` pins. Set `implementation_sha256` to a map from
`solution_diagram__pub.py` and `shape_diagram__pub.py` to their digests.

Translate both source files. Compare the renderer output with the
authored shape in the two configured field orders. For each order,
check a positional call and a call with `action=None`. Report both
call results. Check the Solution request, render effect, and return
guards against the observed path. Report unobserved guards under
`solution_gap` and keep the diagram results. Report an absent
or whitespace-only diagram as a mismatch. A different nonblank layout
stays unresolved. Other renderer behavior and effects need separate evidence.

With `--component C88 --pins`, use Active AN-S-4935@1 and
AN-S-5030@1. The request pins seven implementation files by paths
relative to the Formal Specification code root. The C88 Functional
fixture contains the exact reviewed request.

Translate the declared comparison entry and its bindings. Compare
the three ordered directions in the returned report with the Manifest
and Contract effects and the Solution path in Lean. Check the exact
fact keys, typed values, and verdicts on the fixed mixed input.
Report the wrapper result separately from the expected conflicting
domain verdict. Changed source pins, incomplete result rows, and
unobserved paths leave the witness unresolved.

The witness uses two observed join strings and the output of the
selected Lean executable for the exact worker bytes. Report the model,
worker, and harness digests. Other input shapes, general serialization,
Python consumer visibility, and process effects require separate evidence.
