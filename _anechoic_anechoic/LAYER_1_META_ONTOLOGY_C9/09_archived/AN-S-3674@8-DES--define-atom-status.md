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
  version: 8
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Define Atom Status

# Summary

Define Atom Status

## Scope

Status borne by an Atom, including the recorded value preserved in an archived Atom.

## Claim

Atom.Status **means** the Atom's lifecycle classification under its applicable Status model. Status is a dependent property of the Atom; its allowed values resolve under the applicable Atom, Content Role and Type rules.

## Details

IS_BORNE_BY expresses the property-to-Atom relation. A Current Atom is not historical merely because it has a Version Number. An archived Atom preserves its recorded Status; preserving history does not rewrite that value. CA-R-1412 supplies the one-Status requirement. The separate allowed-value rules define inherited and additional values; this definition adds no values, transition procedure or mandatory history record. Shared Status meanings are derived in the Terms graph from source usage, not independently authored here for every owner.
