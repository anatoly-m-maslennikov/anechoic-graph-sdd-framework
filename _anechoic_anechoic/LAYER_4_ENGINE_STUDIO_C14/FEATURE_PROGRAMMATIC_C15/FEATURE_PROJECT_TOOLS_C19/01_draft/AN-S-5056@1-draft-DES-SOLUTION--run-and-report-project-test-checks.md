---
atom_family: SPEC
atom_id: AN-S-5056
container:
  component: C19
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3055@28-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Run and report Project checks, clean marked scratch directories,
and migrate staged native Atom Headers.

## Claim

### Prose Claim

Discover the required host Modules or use the admitted selection.
Run the Modules in fresh interpreters and collect the individual
results and suite totals. Classify the returned process status as zero
or nonzero.

Preflight calls `suite_preflight.run_preflight` to check the required
frontend, DuckPGQ, and Chromium prerequisites. Report all failed checks
before returning a nonzero status.

Static calls the source analyzers before selecting the static test
Modules. Apply `AN-S-5050@1` and `AN-S-5051@1` to Programmatic source.
Use `AN-S-4739@3` for other source. Report size findings and fail Static
before test selection if the size checker fails.

For Static and Functional, report the phase outcome after the checks.
Image-tests runs only the candidate image tests. Canary runs the
required canary host tests and then verifies the candidate. Combined
Image proceeds to the canary only after the image tests pass.

Record the release test phase status in the Test Suite report before
returning the process status. An earlier check can report a diagnostic
on the output streams before the final report is written.

`prune_private_tmp.main` dispatches mark or cleanup. Mark records the
resolved checkout in the directory's marker. Cleanup checks that the
marker and the directory exceed the retention time and that the
directory is safe to delete. It skips protected paths and reports
each removal.

`migrate_native_atom_headers.run` validates the staging paths and
preflights the carrier mappings before writing. It converts admitted
Headers in a new tree, copies other staged entries, and writes an
adjacent receipt. If an output write fails, it attempts to remove
the destination tree and propagates the failure.

### Formal Claim

```python
component_workflow(
    component='C19',
    action='run_project_test_suite',
    machine={
        'id': 'c19_run_project_test_suite',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'suite_requested': {'target': 'selecting',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'transport': 'cli',
                            'runner': 'uv',
                            'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py',
                        },
                    }}},
            }},
            'selecting': {'on': {
                'phase_admitted': {'target': 'running',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'running',
                    }}},
                'selection_or_environment_refused': {'target': 'failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {
                            'exit_status_class': 'nonzero',
                        },
                    }}},
            }},
            'running': {'on': {
                'suite_passed': {'target': 'succeeded',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'succeeded',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
                'suite_failed': {'target': 'failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {
                            'exit_status_class': 'nonzero',
                        },
                    }}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C19',
    action='run_release_test_phase',
    machine={
        'id': 'c19_run_release_test_phase',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'preflight_selected': {'target': 'preflight_checking',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'preflight',
                        },
                    }}},
                'static_selected': {'target': 'static_testing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'static',
                        },
                    }}},
                'functional_selected': {'target': 'functional_testing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'functional',
                        },
                    }}},
                'image_tests_selected': {'target': 'image_tests_testing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'image-tests',
                        },
                    }}},
                'canary_selected': {'target': 'canary_testing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'canary',
                        },
                    }}},
                'image_selected': {'target': 'image_testing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'test_suite',
                        'detail': {
                            'phase': 'image',
                        },
                    }}},
            }},
            'preflight_checking': {'on': {
                'prerequisite_checks_passed': {'target': 'preflight_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'prerequisite_checks',
                        'outcome': 'passed',
                    }}},
                'preflight_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'preflight_passed': {'on': {
                'phase_passed': {'target': 'reporting_preflight',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_preflight': {'on': {
                'phase_result': {'target': 'returned_preflight_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'preflight_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'static_testing': {'on': {
                'static_checks_passed': {'target': 'static_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'static_checks', 'outcome': 'passed',
                    }}},
                'static_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'static_passed': {'on': {
                'phase_passed': {'target': 'reporting_static',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_static': {'on': {
                'phase_result': {'target': 'returned_static_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'static_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'functional_testing': {'on': {
                'host_functional_checks_passed': {'target': 'functional_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'host_functional_checks', 'outcome': 'passed',
                    }}},
                'functional_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'functional_passed': {'on': {
                'phase_passed': {'target': 'reporting_functional',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_functional': {'on': {
                'phase_result': {'target': 'returned_functional_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'functional_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'image_tests_testing': {'on': {
                'candidate_image_tests_passed': {'target': 'image_tests_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'candidate_image_tests', 'outcome': 'passed',
                    }}},
                'image_tests_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'image_tests_passed': {'on': {
                'phase_passed': {'target': 'reporting_image_tests',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_image_tests': {'on': {
                'phase_result': {'target': 'returned_image_tests_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'image_tests_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'canary_testing': {'on': {
                'canary_host_checks_passed': {'target': 'canary_verifying_canary',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'canary_host_checks', 'outcome': 'passed',
                    }}},
                'canary_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'canary_verifying_canary': {'on': {
                'candidate_canary_passed': {'target': 'canary_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'candidate_canary', 'outcome': 'passed',
                    }}},
                'candidate_canary_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'canary_passed': {'on': {
                'phase_passed': {'target': 'reporting_canary',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_canary': {'on': {
                'phase_result': {'target': 'returned_canary_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'canary_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'image_testing': {'on': {
                'candidate_image_tests_passed': {'target': 'image_verifying_canary',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'candidate_image_tests', 'outcome': 'passed',
                    }}},
                'image_phase_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'image_verifying_canary': {'on': {
                'candidate_canary_passed': {'target': 'image_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'candidate_canary', 'outcome': 'passed',
                    }}},
                'candidate_canary_failed': {'target': 'reporting_failure',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'failed',
                    }}},
            }},
            'image_passed': {'on': {
                'phase_passed': {'target': 'reporting_image',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C19', 'outcome': 'passed',
                    }}},
            }},
            'reporting_image': {'on': {
                'phase_result': {'target': 'returned_image_passed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'image_passed',
                        'detail': {
                            'exit_status_class': 'zero',
                        },
                    }}},
            }},
            'reporting_failure': {'on': {
                'failure_result': {'target': 'returned_failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {
                            'exit_status_class': 'nonzero',
                        },
                    }}},
            }},
            'returned_preflight_passed': {'type': 'final'},
            'returned_static_passed': {'type': 'final'},
            'returned_functional_passed': {'type': 'final'},
            'returned_image_tests_passed': {'type': 'final'},
            'returned_canary_passed': {'type': 'final'},
            'returned_image_passed': {'type': 'final'},
            'returned_failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C19',
    action='clean_project_scratch',
    machine={
        'id': 'c19_clean_project_scratch',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'cleanup_requested': {'target': 'running',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'prune_private_tmp',
                        'detail': {
                            'transport': 'cli',
                            'runner': 'python',
                            'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/prune_private_tmp.py',
                        },
                    }}},
            }},
            'running': {'on': {
                'cleanup_completed': {'target': 'succeeded',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'succeeded',
                        'detail': {'exit_status_class': 'zero'},
                    }}},
                'cleanup_failed': {'target': 'failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {'exit_status_class': 'nonzero'},
                    }}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C19',
    action='migrate_staged_headers',
    machine={
        'id': 'c19_migrate_staged_headers',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'migration_requested': {'target': 'preflighting',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'migrate_native_atom_headers',
                        'detail': {
                            'transport': 'cli',
                            'runner': 'uv',
                            'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/migrate_native_atom_headers.py',
                        },
                    }}},
            }},
            'preflighting': {'on': {
                'request_admitted': {'target': 'writing',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'migration_preflight',
                        'outcome': 'passed',
                    }}},
                'request_refused': {'target': 'failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {'exit_status_class': 'nonzero'},
                    }}},
            }},
            'writing': {'on': {
                'migration_completed': {'target': 'succeeded',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'succeeded',
                        'detail': {'exit_status_class': 'zero'},
                    }}},
                'write_failed': {'target': 'failed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                        'detail': {'exit_status_class': 'nonzero'},
                    }}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
