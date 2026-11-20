---
identity:
  atom_id: AN-T-2743
context:
  container:
    atom: AN-T-2483
  tier: 3
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-13T19:14:23.654988+00:00'
---
## Summary

Migrate Relation Declarations to endpoint applicability

## Work

Migrate the live Relation Declarations to the approved endpoint-level rules. Preserve intentional Model-only, instance-only, and cross-level endpoints. Keep inverse aliases tied to the same fact. Update the ordering declarations and align the Node Property rules with the endpoint levels. Check canonical source coverage and coordinate with CA-P-3060.

## Specification

CA-R-2247, CA-R-2965, CA-R-2476, CA-R-2473, CA-R-2462, CA-R-3083.

## Progress

Active CA-R-2476@9 declares the instance-to-Model endpoints and HAS_INSTANCE inverse alias. Active CA-R-2473@7 declares same-level endpoint pairs for Model Properties and Property instances. Active CA-R-2965@3 declares instance-only sibling ordering. CA-R-2462@7 reflects that scope. The redundant CA-R-2619 is Archived.

1. Build and verify the Relation registry from canonical Declarations. Register inverse aliases before validating references and keep paired endpoint signatures together. CA-R-1580, CA-R-2420, CA-R-2617 and CA-R-2767 are Archived. Their canonical owners preserve the existing aliases.
2. Migrate Entity Declarations against that registry. Check their local Relation constraints against the registered endpoint pairs and Python class inheritance before generating the classes.
