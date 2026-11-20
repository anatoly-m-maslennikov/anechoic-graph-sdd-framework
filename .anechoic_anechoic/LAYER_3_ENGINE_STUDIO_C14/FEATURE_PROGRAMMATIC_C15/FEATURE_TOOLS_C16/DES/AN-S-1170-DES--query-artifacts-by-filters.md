---
identity:
  atom_id: AN-S-1170
context:
  container:
    component: C16
  tier: 1
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Query artifacts by filters

# Query artifacts by filters

the framework **must** provide one deterministic generic Artifact Tool that returns stably ordered canonical artifact IDs **and** carrier paths matching composable filters for structural scope, layer, tier, Feature, Content role, subject scope, lifecycle state, **and** typed relations **without** loading artifact bodies.

this Tool owns generic artifact-query mechanics **only**. `ATOM_SEARCH` owns ANECHOIC Markdown Atom eligibility, selector, lifecycle, subtree, content-query, **and** output-view semantics; it **may** use this Tool as a helper but the generic Tool **must not** become the public Atom-search operation.
