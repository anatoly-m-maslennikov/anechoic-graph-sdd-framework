# Applicable Principles

Each number also appears in its linked source Atom. The Atoms contain the authoritative Claims.

Each Principle shows its authored support relations and the Axioms it applies. The [Tier 1 design](../_anechoic_anechoic/__TICKETS/TASKS/AN-T-2932-TASK--admit-project-axioms-project-contracts-and-applicable-principles.md) says Tier 1 Principles serve the Project Goal.

## Contents

- [Operator authority and delegation](#operator-authority-and-delegation)
- [Project structure and scope](#project-structure-and-scope)
- [Project information and context](#project-information-and-context)
- [Specification language](#specification-language)
- [Decision evidence and oversight](#decision-evidence-and-oversight)
- [Verification and rework](#verification-and-rework)
- [Reuse and efficiency](#reuse-and-efficiency)
- [Framework configuration and evolution](#framework-configuration-and-evolution)


# Project Practice


## Operator authority and delegation


### 1.1 Keep full authority and control with the Operator


[AN-S-1438](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1438-DES-APPLICABLE_PRINCIPLE--keep-full-authority-and-control-with-the-operator.md)

> The Operator has the final say over the Project and its ANECHOIC instance. The Operator can delegate authority to AI Agents, change it, or withdraw it, and can observe, guide, stop, and recover important work.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.


### 1.2 Do not require human participants to master or personally perform specialist work


[AN-S-1449](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1449-DES-APPLICABLE_PRINCIPLE--do-not-require-human-participants-to-master-or-personally-perform-specialist-work.md)

> Let the Operator create, deliver, run, and maintain a feasible Project without having to master or personally perform its specialist work.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.1 — Directing specialist work does not require mastering the craft](../_anechoic_anechoic/AN-S-1448-SPEC-AXIOM--directing-specialist-work-does-not-require-mastering-the-craft.md).


### 1.3 Give Operators clear guidance for using the framework


[AN-S-1453](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1453-DES-APPLICABLE_PRINCIPLE--give-operators-clear-guidance-for-using-the-framework.md)

> Provide the Operator with enough clear guidance to use the framework efficiently toward their Project goals.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.


### 1.4 Delegate decisions that can tolerate surprises


[AN-S-1474](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1474-SWD-APPLICABLE_PRINCIPLE--delegate-decisions-that-can-tolerate-surprises.md)

> Let AI Agents make decisions where an unexpected result is acceptable.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.2 — Delegating judgment to AI Agents saves Operator effort but makes results less predictable](../_anechoic_anechoic/AN-S-1473-SPEC-AXIOM--delegating-judgment-to-ai-agents-saves-operator-effort-but-makes-results-less-predictable.md).


### 1.5 Reserve the Operator’s attention for key decisions


[AN-S-1475](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1475-SWD-APPLICABLE_PRINCIPLE--reserve-the-operator-s-attention-for-key-decisions.md)

> Save the Operator’s time and attention for decisions where their judgment matters most.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.2 — Delegating judgment to AI Agents saves Operator effort but makes results less predictable](../_anechoic_anechoic/AN-S-1473-SPEC-AXIOM--delegating-judgment-to-ai-agents-saves-operator-effort-but-makes-results-less-predictable.md).

---


## Project structure and scope


### 2.1 MECE — Cover the whole with non-overlapping parts


[AN-S-1441](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1441-SWD-APPLICABLE_PRINCIPLE--mece-cover-the-whole-with-non-overlapping-parts.md)

> When we split something into parts, include everything within the chosen boundaries and put each item in only one part.

**Tier 1 purpose** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md). This Atom has no authored direct support relation.

**Applies** [1.3 — Clear structure and ownership make information easier to maintain](../_anechoic_anechoic/AN-S-1432-SPEC-AXIOM--clear-structure-and-ownership-make-information-easier-to-maintain.md).


### 2.2 Represent systems through explicit graphs


[AN-S-1442](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1442-SWD-APPLICABLE_PRINCIPLE--represent-systems-through-explicit-graphs.md)

> Represent Project decisions, structure, artifacts, and other objects as connected graphs. Use their connections to find information, trace the effects of changes, and support checks.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [1.2 — Information can be managed at any scale](../_anechoic_anechoic/AN-S-1428-SPEC-AXIOM--information-can-be-managed-at-any-scale.md).


### 2.3 Break work into scopes small enough to reason about


[AN-S-1485](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1485-SWD-APPLICABLE_PRINCIPLE--break-work-into-scopes-small-enough-to-reason-about.md)

> Give each task a clear boundary and keep its dependencies easy to find. That lets people and agents work on one part without losing how it fits into the whole.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [1.1 — Operators and AI Agents can only work with so much context at once](../_anechoic_anechoic/AN-S-1484-SPEC-AXIOM--operators-and-ai-agents-can-only-work-with-so-much-context-at-once.md).


### 2.4 Prefer fractal structures with minimal exceptions


[AN-S-3190](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-3190-SPEC-APPLICABLE_PRINCIPLE--prefer-fractal-structures-with-minimal-exceptions.md)

> When you organize a structure, try to use the same rules at each level,
> with minimal exceptions.

**Tier 1 purpose** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md). This Atom has no authored direct support relation.

**Applies** [1.3 — Clear structure and ownership make information easier to maintain](../_anechoic_anechoic/AN-S-1432-SPEC-AXIOM--clear-structure-and-ownership-make-information-easier-to-maintain.md).


### 2.5 Constrain Project graph edges by hierarchy and type


[AN-S-4802](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-4802-SWD-APPLICABLE_PRINCIPLE--constrain-project-graph-edges-by-hierarchy-and-type.md)

> Prefer a hierarchical Project graph with typed nodes and relations. Minimize the number of allowed edges while keeping those the Project needs. Use endpoint types and scope to limit which edges are allowed.

**Tier 1 purpose** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md). This Atom has no authored direct support relation.

**Applies** [1.3 — Clear structure and ownership make information easier to maintain](../_anechoic_anechoic/AN-S-1432-SPEC-AXIOM--clear-structure-and-ownership-make-information-easier-to-maintain.md).

---


## Project information and context


### 3.1 Work with the specification as a collection of Operators’ decisions


[AN-S-1439](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1439-SWD-APPLICABLE_PRINCIPLE--work-with-the-specification-as-a-collection-of-operators-decisions.md)

> Treat the Spec as a collection of decisions made by Operators or by AI Agents acting under their authority. Record every decision that matters to the Project, why it was made, and the facts and assumptions that mattered.
>
> When a similar choice comes up, the AI Agent reads the Spec to recover the context. If the relevant conditions still hold, it can reuse the Operator’s decision.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [1.1 — Operators and AI Agents can only work with so much context at once](../_anechoic_anechoic/AN-S-1484-SPEC-AXIOM--operators-and-ai-agents-can-only-work-with-so-much-context-at-once.md).


### 3.2 SST — Keep a Single Source of Truth


[AN-S-1446](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1446-SWD-APPLICABLE_PRINCIPLE--sst-keep-a-single-source-of-truth.md)

> Keep one source of truth for each piece of Project information. Make copies from that source instead of editing each copy separately.

**Tier 1 purpose** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md). This Atom has no authored direct support relation.

**Applies** [1.3 — Clear structure and ownership make information easier to maintain](../_anechoic_anechoic/AN-S-1432-SPEC-AXIOM--clear-structure-and-ownership-make-information-easier-to-maintain.md).


### 3.3 Expose only task necessary distinctions


[AN-S-1476](../_anechoic_anechoic/_DES/AN-S-1476-DES-APPLICABLE_PRINCIPLE--expose-only-task-necessary-distinctions.md)

> ANECHOIC **must** expose **to** the Operator **only** the distinctions necessary **to** understand **and** control the current task.

**Supports** [Principle 3.5 — Show what is needed; keep the rest](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1486-SWD-APPLICABLE_PRINCIPLE--show-what-is-needed-keep-the-rest.md) through `CONTRIBUTES_TO`.


### 3.4 Preserve valuable information


[AN-S-1478](../_anechoic_anechoic/_DES/AN-S-1478-DES-APPLICABLE_PRINCIPLE--preserve-valuable-information.md)

> Keep valuable Project information in durable, reliable storage so it remains recoverable across sessions, handoffs, context loss, and implementation changes.

**Supports** [Principle 3.5 — Show what is needed; keep the rest](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1486-SWD-APPLICABLE_PRINCIPLE--show-what-is-needed-keep-the-rest.md) through `CONTRIBUTES_TO`.


### 3.5 Show what is needed; keep the rest


[AN-S-1486](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1486-SWD-APPLICABLE_PRINCIPLE--show-what-is-needed-keep-the-rest.md)

> Show enough information for the current task without unnecessary context. Keep other retained information recoverable.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [1.1 — Operators and AI Agents can only work with so much context at once](../_anechoic_anechoic/AN-S-1484-SPEC-AXIOM--operators-and-ai-agents-can-only-work-with-so-much-context-at-once.md).


### 3.6 Keep only necessary and sufficient reusable project information


[AN-S-1863](../_anechoic_anechoic/_SWD/AN-S-1863-SWD-APPLICABLE_PRINCIPLE--keep-only-necessary-and-sufficient-reusable-project-information.md)

> Keep only the reusable information needed to understand, govern, operate, and change the Project.

**Supports** [Principle 3.5 — Show what is needed; keep the rest](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1486-SWD-APPLICABLE_PRINCIPLE--show-what-is-needed-keep-the-rest.md) through `CONTRIBUTES_TO`.

---


## Specification language


### 4.1 Use familiar concepts with their usual meanings


[AN-S-1953](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1953-SWD-APPLICABLE_PRINCIPLE--use-familiar-concepts-with-their-usual-meanings.md)

> Prefer concepts and terms that people and AI Agents already understand. Use familiar terms with their usual meanings.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [3.1 — Do not reinvent the wheel](../_anechoic_anechoic/AN-S-1951-SPEC-AXIOM--do-not-reinvent-the-wheel.md).


### 4.2 Give every specification term one clear job


[AN-S-2811](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-2811-SWD-APPLICABLE_PRINCIPLE--give-every-specification-term-one-clear-job.md)

> Name the exact thing or relationship you mean. If a keyword can mean several different things in the same specification, replace it with distinct names. A person, an AI Agent, and a tool should not have to guess which meaning applies.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.


### 4.3 Avoid words so overloaded they say almost nothing


[AN-S-2812](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-2812-SWD-APPLICABLE_PRINCIPLE--avoid-words-so-overloaded-they-say-almost-nothing.md)

> Do not choose a term that already means too many different things. Choose a name that tells readers what something is or how it relates to other things, without making them look up what the word means here.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

---


## Decision evidence and oversight


### 5.1 Keep decisions, work, and outcomes traceable


[AN-S-1440](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1440-SWD-APPLICABLE_PRINCIPLE--keep-decisions-work-and-outcomes-traceable.md)

> Link decisions to their reasons, the work based on them, and the results observed. Keep enough history to follow those links as the Project changes.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.3 — Transparency supports informed control](../_anechoic_anechoic/AN-S-1435-SPEC-AXIOM--transparency-supports-informed-control.md).


### 5.2 Make Project state and ongoing work visible


[AN-S-1443](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1443-SWD-APPLICABLE_PRINCIPLE--make-project-state-and-ongoing-work-visible.md)

> Show what is running, what has changed, what is blocked or failing, and what resources are being used.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.3 — Transparency supports informed control](../_anechoic_anechoic/AN-S-1435-SPEC-AXIOM--transparency-supports-informed-control.md).


### 5.3 Make the basis of decisions and actions understandable


[AN-S-1444](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1444-SWD-APPLICABLE_PRINCIPLE--make-the-basis-of-decisions-and-actions-understandable.md)

> Show which Project information, instructions, and permissions guide important actions. Explain recorded decisions in plain language.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.3 — Transparency supports informed control](../_anechoic_anechoic/AN-S-1435-SPEC-AXIOM--transparency-supports-informed-control.md).


### 5.4 Give the Operator enough information to decide


[AN-S-1458](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1458-DES-APPLICABLE_PRINCIPLE--give-the-operator-enough-information-to-decide.md)

> Provide the Operator with the relevant information needed for Project decisions, without unnecessary detail.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [2.3 — Transparency supports informed control](../_anechoic_anechoic/AN-S-1435-SPEC-AXIOM--transparency-supports-informed-control.md).


### 5.5 Let the Operator inspect framework execution


[AN-S-1855](../_anechoic_anechoic/_DES/AN-S-1855-DES-APPLICABLE_PRINCIPLE--let-the-operator-inspect-framework-execution.md)

> Give the Operator access to relevant framework execution evidence and known limitations.

**Supports** [Principle 5.2 — Make Project state and ongoing work visible](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1443-SWD-APPLICABLE_PRINCIPLE--make-project-state-and-ongoing-work-visible.md) through `CONTRIBUTES_TO`.

---


## Verification and rework


### 6.1 Require usable inputs for reliance


[AN-S-1081](../_anechoic_anechoic/_QA/AN-S-1081-QA-APPLICABLE_PRINCIPLE--require-usable-inputs-for-reliance.md)

> a governed conclusion **may** be treated as reliable for an affected use **only** **when** **every** required input is present, known, consistent, **and** valid.

**Supports** [Principle 5.4 — Give the Operator enough information to decide](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1458-DES-APPLICABLE_PRINCIPLE--give-the-operator-enough-information-to-decide.md) through `CONTRIBUTES_TO`.


### 6.2 Prioritize problems by the rework they can cause


[AN-S-1487](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1487-SWD-APPLICABLE_PRINCIPLE--prioritize-problems-by-the-rework-they-can-cause.md)

> Put the most effort into early checks and lasting fixes where a problem would force the most downstream work to be redone.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [3.5 — Shift Left: Problems cost less when addressed before they spread](../_anechoic_anechoic/AN-S-1434-SPEC-AXIOM--shift-left-problems-cost-less-when-addressed-before-they-spread.md).


### 6.3 Test costly assumptions before building on them


[AN-S-1488](../_anechoic_anechoic/_SWD/AN-S-1488-SWD-APPLICABLE_PRINCIPLE--test-costly-assumptions-before-building-on-them.md)

> Check assumptions that would force substantial rework if wrong.

**Supports** [Principle 6.2 — Prioritize problems by the rework they can cause](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1487-SWD-APPLICABLE_PRINCIPLE--prioritize-problems-by-the-rework-they-can-cause.md) through `CONTRIBUTES_TO`.


### 6.4 Make governed commitments and results checkable


[AN-S-1501](../_anechoic_anechoic/_QA/AN-S-1501-QA-APPLICABLE_PRINCIPLE--make-governed-commitments-and-results-checkable.md)

> Before relying on a work commitment or result, establish a usable way to check it.

**Supports** [Principle 5.1 — Keep decisions, work, and outcomes traceable](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1440-SWD-APPLICABLE_PRINCIPLE--keep-decisions-work-and-outcomes-traceable.md) through `CONTRIBUTES_TO`.

---


## Reuse and efficiency


### 7.1 DRY — Don’t Repeat Yourself


[AN-S-1445](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1445-SWD-APPLICABLE_PRINCIPLE--dry-don-t-repeat-yourself.md)

> Avoid repeating the same information or logic unnecessarily.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.


### 7.2 Reduce the overhead of applying the framework


[AN-S-1451](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1451-DES-APPLICABLE_PRINCIPLE--reduce-the-overhead-of-applying-the-framework.md)

> Apply the framework using fewer LLM tokens, less Operator effort, and less waiting time, without weakening required Project outcomes.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [3.4 — Repeated work becomes more efficient through automation](../_anechoic_anechoic/AN-S-1436-SPEC-AXIOM--repeated-work-becomes-more-efficient-through-automation.md).


### 7.3 Prefer well-known technologies and interfaces


[AN-S-1952](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1952-SWD-APPLICABLE_PRINCIPLE--prefer-well-known-technologies-and-interfaces.md)

> Prefer technologies and interfaces that AI Agents already know. Use custom ones when their value justifies the extra learning and maintenance.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.

**Applies** [3.2 — Figure out what wheel you need then adopt the best one that fits](../_anechoic_anechoic/AN-S-2810-SPEC-AXIOM--figure-out-what-wheel-you-need-then-adopt-the-best-one-that-fits.md).

---


## Framework configuration and evolution


### 8.1 Make framework behavior configurable


[AN-S-1430](../_anechoic_anechoic/_DES/AN-S-1430-DES-APPLICABLE_PRINCIPLE--make-framework-behavior-configurable.md)

> Let the Operator inspect and change the framework’s effective configuration. Supported behavior can be selected through explicit configuration without changing the implementation.

**Supports** [Principle 1.1 — Keep full authority and control with the Operator](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1438-DES-APPLICABLE_PRINCIPLE--keep-full-authority-and-control-with-the-operator.md) through `CONTRIBUTES_TO`.


### 8.2 Keep every part of the framework open to change


[AN-S-1433](../_anechoic_anechoic/_DES/AN-S-1433-DES-APPLICABLE_PRINCIPLE--keep-every-part-of-the-framework-open-to-change.md)

> The Operator can change any part of their ANECHOIC instance to meet the Project’s needs.

**Supports** [Principle 1.1 — Keep full authority and control with the Operator](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1438-DES-APPLICABLE_PRINCIPLE--keep-full-authority-and-control-with-the-operator.md) through `CONTRIBUTES_TO`.


### 8.3 Extend the framework without changing its core


[AN-S-1491](../_anechoic_anechoic/_DES/AN-S-1491-DES-APPLICABLE_PRINCIPLE--extend-the-framework-without-changing-its-core.md)

> Let the Operator add capabilities without having to change the framework’s core.

**Supports** [Principle 1.1 — Keep full authority and control with the Operator](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-1438-DES-APPLICABLE_PRINCIPLE--keep-full-authority-and-control-with-the-operator.md) through `CONTRIBUTES_TO`.


### 8.4 Rebuild Implementation from its governing specification


[AN-S-2451](../_anechoic_anechoic/01_TIER_1_ARCHITECTURE/AN-S-2451-SWD-APPLICABLE_PRINCIPLE--rebuild-implementation-from-its-governing-specification.md)

> **Scope**
>
> The creation or evolution of this Project's Implementation.
>
> Keep ANECHOIC’s specification complete enough to rebuild the framework without relying on its current implementation.

**Supports** [AN-S-1233 — Project Goal](../AN-S-1233-SPEC-PROJECT_GOAL--create-and-evolve-a-working-anechoic-framework.md) through `SERVES`.
