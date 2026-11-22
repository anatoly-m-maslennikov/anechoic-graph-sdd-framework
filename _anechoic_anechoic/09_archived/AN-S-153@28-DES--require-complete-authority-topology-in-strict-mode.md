---
atom_family: SPEC
atom_id: AN-S-153
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: '2026-11-22T10:50:06.341674+00:00'
---
## Summary
Require complete authority topology in strict mode

## Claim

### Prose Claim


a scope **in** strict authority mode **must** maintain a complete, conflict-free active PRMEDO authority topology with these constraints:

- **every** local Tier 0 Atom **and** Core has **`>=1`** permitted active child **unless** the applicable Type authority registers its Type as terminal;
- the normative-authority subgraph is acyclic under CA-R-833;
- **every** edge follows the tier **and** structural-direction rules applicable **to** its graph kind **and** Relation Kind; **and**
- an Active RMED Atom's direct relation **to** an RMED Atom requires an Active target under ANECHOIC-GOV-REQU-767. other endpoint classes retain the Status constraints of their own governing Relation authority.

the authority-subgraph acyclicity constraint does **not** impose acyclicity on **every** other graph, including Workflow control flow.
