---
atom_family: SPEC
atom_id: AN-S-3549
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-10-26 05:25:17 +0400
---
## Summary

Define Subject Target Roots

# Summary

Define Subject Target Roots

## Scope

canonical Subject paths in this model.

## Claim

Bare Subject is the valid umbrella. Every more-specific canonical Subject path starts at Subject and then enters exactly one root branch: Graph Node, Graph Relation, or Graph Rule. Graph Node contains the canonical target hierarchy. Its categories are open: Continuant, Occurrent and Aspect are admitted examples, not an exhaustive list. Domain and Engineering each have Continuant and Occurrent child branches; Documentation, Product, and UX are also current Graph Node branches, and that set is expandable. Graph Relation names relation topics and Graph Rule names graph-constraint topics.

## Details

Graph Node is a Subject-path branch, not a new Entity, Carrier, intermediate Subject object, or target identity. Product names what the project produces; Domain names the concepts and things it works with; Engineering names how it is built, stored, and operated. Branch assignment distinguishes modeled work in Domain (Action, Step, and Workflow Run) from technical runtime in Engineering (Session and tool/app runtimes). Other Engineering policy or pure topics may remain directly under Engineering; no target acquires a temporal classification merely from this taxonomy. Continuant, Occurrent and Aspect are category examples, not a closed enum. UX names the MCP interface and health-page appearance; it does not reclassify backend Engineering or MCP topics wholesale. Documentation retains its topic meaning.

Subject branch, Content Role and Local Scope Unit are independent. A Requirement about a product can live at Project scope without making Project its Subject. A topic need not be an independently carried object. A Scope Unit path is not automatically a Subject path.
