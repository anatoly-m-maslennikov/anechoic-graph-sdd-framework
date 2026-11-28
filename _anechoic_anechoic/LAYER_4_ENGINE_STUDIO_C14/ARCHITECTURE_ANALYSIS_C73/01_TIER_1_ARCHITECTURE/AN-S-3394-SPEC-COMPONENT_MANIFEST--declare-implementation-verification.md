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
  status: active
  version: 19
  updated_at: "2026-11-28T15:09:14+00:00"
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
{'code': {'imports': {'only': [
                               'analysis.analysis__shared.python_code_units','components__shared.component_contract_fences', 'components__shared.parse_component_manifest', 'content__shared.formal_claim_fences', 'content__shared.frontmatter_bounds', 'content__shared.parse_carrier', 'content__shared.source_body', 'WORKERS_beta_C69__shared.python_code_units',
                               'ADAPTERS_C30__shared.frontmatter_bounds',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.parse_carrier',
                               'ADAPTERS_C30__shared.parse_component_manifest',
                               'ADAPTERS_C30__shared.formal_claim_fences',
                               'ADAPTERS_C30__shared.component_contract_fences',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.generate_framing_cases',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared.lean_string',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared.parse_contract',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared.manifest_tool_api',
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.verify_formal_chain',
                               'http.http__shared.extract_backend_checks',
                               'http.backend_http_contract.contract_to_lean',
                               'http.backend_http_source.extract_http_observations',
                               'http._backend_http_compare_formal._compare_formal',
                               'carrier.carrier__shared.compare_direct',
                               'carrier.carrier_observations.lean_bytes',
                               'carrier.carrier_observations.observe',
                               'carrier.carrier_observations.python_checks',
                               'c88.c88__shared.compare_c88',
                               'diagnostics.diagnostics__shared.compare_diagnostic',
                               'shape_renderer.shape_renderer__shared.RENDERER_SOURCE_NAMES',
                               'shape_renderer.shape_renderer__shared.compare_renderer',
                               'diagnostics.diagnostics__shared._execute',
                               'export_binding.export_check',
                               'export_binding.export_pin',
                               'backend_http_compare._actual',
                               'backend_http_compare._checks_report',
                               'backend_http_compare._run_lean',
                               'carrier._carrier_compare_helpers._CASES',
                               'carrier._carrier_compare_helpers._checks',
                               'carrier._carrier_compare_helpers._findings',
                               'carrier._carrier_compare_helpers._formal_program',
                               'carrier._carrier_compare_helpers._formal_report',
                               'carrier._carrier_compare_helpers._valid_formal_values',
                               'http.backend_http_formal._carrier',
                               'http.backend_http_formal._facts',
                               'shape_renderer.shape_implementation.compare',
                               'carrier_compare.compare',
                               'carrier.carrier_model._SOURCE',
                               'carrier.carrier_model.generate',
                               'carrier.carrier_runtime_effects',
                               'carrier.carrier_runtime_effects.analyze_carrier',
                               'carrier.carrier_formal._PATHS',
                               'carrier.carrier_formal.formal_inputs']},
          'exports': {'carrier.carrier_runtime_effects.analyze_carrier': {'private': ['C74']},
                      'http.http__shared.extract_backend_checks': {'private': ['C74']},
                      'http.backend_http_contract.contract_to_lean': {'private': ['C74']},
                      'http.backend_http_source.extract_http_observations': {'private': ['C74']},
                      'http._backend_http_compare_formal._compare_formal': {'private': ['C74']},
                      'carrier.carrier__shared.compare_direct': {'private': ['C74']},
                      'carrier.carrier_observations.lean_bytes': {'private': ['C74']},
                      'carrier.carrier_observations.observe': {'private': ['C74']},
                      'carrier.carrier_observations.python_checks': {'private': ['C74']},
                      'c88.c88__shared.compare_c88': {'private': ['C74']},
                      'diagnostics.diagnostics__shared.compare_diagnostic': {'private': ['C74']},
                      'shape_renderer.shape_renderer__shared.RENDERER_SOURCE_NAMES': {'private': ['C74']},
                      'shape_renderer.shape_renderer__shared.compare_renderer': {'private': ['C74']},
                      'diagnostics.diagnostics__shared._execute': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/c88', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/shape_renderer']},
                      'export_binding.export_check': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/diagnostics', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/shape_renderer']},
                      'export_binding.export_pin': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/diagnostics', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/shape_renderer']},
                      'backend_http_compare._actual': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/http']},
                      'backend_http_compare._checks_report': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/http']},
                      'backend_http_compare._run_lean': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/http']},
                      'carrier._carrier_compare_helpers._CASES': {'private': ['C74']},
                      'carrier._carrier_compare_helpers._checks': {'private': ['C74']},
                      'carrier._carrier_compare_helpers._findings': {'private': ['C74']},
                      'carrier._carrier_compare_helpers._formal_program': {'private': ['C74']},
                      'carrier._carrier_compare_helpers._formal_report': {'private': ['C74']},
                      'carrier._carrier_compare_helpers._valid_formal_values': {'private': ['C74']},
                      'http.backend_http_formal._carrier': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'http.backend_http_formal._facts': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'shape_renderer.shape_implementation.compare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/shape_comparison']},
                      'carrier_compare.compare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/carrier_comparison']},
                      'carrier.carrier_model._SOURCE': {'private': ['C74', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/carrier_comparison']},
                      'carrier.carrier_model.generate': {'private': ['C74', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/carrier_comparison']},
                      'carrier.carrier_runtime_effects': {'private': ['C74', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier.carrier_formal._PATHS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/carrier_comparison']},
                      'carrier.carrier_formal.formal_inputs': {'private': ['C74', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/carrier_comparison']}}},
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

Python Autoform checks relative imports in the selected source tree.
If an import would bind to a shorter staged path or a module below the
wrong root, report the importer, requested path, and candidate file.
Leave ordinary missing imports unresolved.

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
Check the pinned C90 verdict Contract and Solution against the shared
export for every modeled heap-backed list of strings. Report the
theorem, proof digest, and authored Lean digest under `verdict_proof`.
If the verdict proof fails, keep checked findings and leave the result
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
