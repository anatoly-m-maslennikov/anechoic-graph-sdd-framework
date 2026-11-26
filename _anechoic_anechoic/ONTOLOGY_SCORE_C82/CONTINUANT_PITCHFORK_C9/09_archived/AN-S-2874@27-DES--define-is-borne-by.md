---
atom_family: SPEC
atom_id: AN-S-2874
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 27
  updated_at: 2026-10-27 19:59:52 +0400
---
## Summary

Define IS_BORNE_BY

# Summary

Define IS_BORNE_BY

## Scope

an IS_BORNE_BY Relation from Entity A **to** Entity B **in** the Entities Graph.

## Claim

an IS_BORNE_BY Relation from Entity A **to** Entity B **in** the Entities Graph **means** that A is a Dependent Entity whose identity requires B as its immediate bearer.

## Semantics

Primary means that identity does not require another Entity occurrence as bearer. Dependent means that identity requires an immediate bearer, as expressed by IS_BORNE_BY. These describe bearer dependence, not additional taxonomy branches. An absent edge in an incomplete view does not establish independence.
