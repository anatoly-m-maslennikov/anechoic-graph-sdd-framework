---
atom_family: SPEC
atom_id: AN-S-3186
container:
  component: C62
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3088
state:
  status: draft
  version: 5
  updated_at: '2026-11-25T10:58:34Z'
---

## Summary

Serve the compiled Model and Structure

## Guarantee

For a selected native Project, host the admitted Model and validated
Structure in the Kernel process. Provide the compiled Model directory,
bound Model, and Structure snapshot path after verifying that the Model
and initial Structure share one Model source fingerprint.

Run the Manifest Builder in a bounded separate process. On relevant
Manifest changes, validate each replacement Structure against the admitted
Model and publish it atomically. Keep the last accepted Structure if a
rebuild fails. Admit a changed Model on restart.

## Claim

### Prose Claim

For the initial generation, admit the Project and wait for the Worker to
complete. Verify the compiler-attested descriptor and Model module bytes.
Verify the shared Model fingerprint before accepting and publishing the
artifacts. Report failure if the Worker fails or validation fails.

For a Structure refresh, use the admitted Model and publish the replacement
atomically after a Worker completes and the fingerprint matches. If
compilation or validation fails, retain the previous valid snapshot.

### Formal Claim

```python trace
declare_trace_contract(
    action='manifest_runtime_start',
    output='succeeded',
    must_effect=(('C62.project_binding', 'admitted'),
                 ('C66.worker_run', 'completed'),
                 ('C62.model_attestation', 'verified'),
                 ('C62.fingerprint', 'verified'),
                 ('C62.artifacts', 'accepted'),
                 ('C62.structure', 'published')),
    must_precede=((('C62.project_binding', 'admitted'), ('C66.worker_run', 'completed')),
                  (('C66.worker_run', 'completed'), ('C62.model_attestation', 'verified')),
                  (('C66.worker_run', 'completed'), ('C62.fingerprint', 'verified')),
                  (('C62.model_attestation', 'verified'), ('C62.artifacts', 'accepted')),
                  (('C62.fingerprint', 'verified'), ('C62.artifacts', 'accepted')),
                  (('C62.artifacts', 'accepted'), ('C62.structure', 'published'))),
)
```

```python trace
declare_trace_contract(
    action='manifest_runtime_start',
    output='failed',
    forbid_effect=('C62.artifacts', 'C62.structure'),
)
```

```python trace
declare_trace_contract(
    action='manifest_runtime_refresh_structure',
    output='succeeded',
    must_effect=(('C62.admitted_model', 'pinned'),
                 ('C66.worker_run', 'completed'),
                 ('C62.refresh_fingerprint', 'verified'),
                 ('C62.structure_replacement', 'published_atomically')),
    forbid_effect=('C62.model_replacement',),
    must_precede=((('C62.admitted_model', 'pinned'), ('C66.worker_run', 'completed')),
                  (('C66.worker_run', 'completed'), ('C62.refresh_fingerprint', 'verified')),
                  (('C62.refresh_fingerprint', 'verified'), ('C62.structure_replacement', 'published_atomically'))),
)
```

```python trace
declare_trace_contract(
    action='manifest_runtime_refresh_structure',
    output='failed',
    must_effect=(('C62.previous_structure', 'retained'),),
    forbid_effect=('C62.structure_replacement', 'C62.model_replacement'),
)
```

## Details

The trace covers initial generation and Structure refresh outcomes. Exact
fingerprint equality, snapshot identity, and restart behavior remain open.
