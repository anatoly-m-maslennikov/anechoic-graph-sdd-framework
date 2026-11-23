---
atom_family: SPEC
atom_id: AN-S-2510
container:
  component: C9
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 28
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Derive Canonical Scope Signatures **without** Source Rewrite

## Claim

### Prose Claim


derivation of Canonical Scope Signatures from one caller-selected Atom Carrier folder.


**to** derive Canonical Scope Signatures from one caller-selected Atom Carrier folder, the Tool **must** inspect **only** active Carriers with **`=1`** unwrapped Scope Expression **in** one `## Scope` section, resolve **every** atomic identity against active Atom IDs **in** that selected folder, derive a signature **only** **if** the Scope Expression satisfies the restricted Canonical Scope Signature grammar, emit source identity, source revision, source Carrier digest, source frontier digest, source expression, signature, **and** exclusion diagnostic, **and** make no source-Carrier rewrite, lifecycle change, Claim merge, authority decision, **or** dependency relation.
