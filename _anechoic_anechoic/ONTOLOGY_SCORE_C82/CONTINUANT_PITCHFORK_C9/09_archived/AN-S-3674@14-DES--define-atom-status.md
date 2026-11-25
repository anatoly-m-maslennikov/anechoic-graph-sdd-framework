---
atom_family: SPEC
atom_id: AN-S-3674
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-29 09:06:21 +0400
---
## Summary

Define Atom Status

## Claim scope

Status borne by an Atom, including the lifecycle value carried by an archived representation.

## Claim

Atom.Status **means** the Atom's lifecycle classification under its applicable Status model. Status is a dependent property of the Atom; its allowed values resolve under the applicable Atom, Content Role and Type rules. An archived representation carries `Archived` as its status, while retaining the predecessor's Version and Updated At; archiving alone does not create a new version.

### Formal claim

```text
Atom.Status[string]{1}
```

## Details

IS_BORNE_BY expresses the property-to-Atom relation. A Current Atom is not historical merely because it has a Version Number. Archive conversion changes the representation status to `Archived` without changing the governed content, Version or Updated At. CA-R-1412 supplies the one-Status requirement. The separate allowed-value rules define inherited and additional values; this definition adds no values, transition procedure or mandatory history record. Shared Status meanings are derived in the Terms graph from source usage, not independently authored here for every owner.
