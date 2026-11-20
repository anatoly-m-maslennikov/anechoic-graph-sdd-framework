---
identity:
  atom_id: AN-S-2575
context:
  container:
    component: C9
  tier: 3
  lens: SWD
state:
  status: active
  version: 2
  updated_at: '2026-11-13T19:07:32.840362+00:00'
---
## Summary

Assign Atom Topics from complete content

## Claim

### Prose Claim


Topic assignment for an Atom from its Claim **and** complete Markdown Main Content.


**to** assign an Atom's Topics, the Author **must** perform **all** of:

1. read the entire Markdown Main Content, including Summary, Scope, Claim, Details, other registered sections, nested headings, tables, examples, **and** reference labels. build an inventory of canonical Topic target mentions with exact locations **and** full resolved paths. treat an Atom citation label rendered under `CA-M-1024-CORE_META_MODEL-IMPLEMENTATION_METHOD--make-atom-claims-clear-and-preserve-their-meaning` as the referenced Atom's complete filename **without** its `.md` extension **or** directory path. under `CA-R-1280-CORE_META_MODEL-RULE--reference-every-prerequisite-subject-through-depends-on`, the label is readable reference evidence, **not** a Topic target mention **or** Topic target, including **when** it occurs **in** the same sentence as Topic target language; inventory a Topic target **only** **when** surrounding prose independently uses it.

   recognize an evidenced reusable Term through its authoritative Method Atom of Type Term Definition, including the lexical Term `Term` at `Term//Term`. `Evaluation` remains a Term **when** used inside an Evaluation Atom. use structural definitions, such as `CA-R-1318-CORE_META_MODEL-DECLARATION--define-term` for the Term kind and `CA-R-2514-CORE_META_MODEL-DECLARATION--declare-atom-role-evaluation` for the Evaluation Content Role, together with the usage context to resolve the referenced Entity target; those structural definitions do **not** replace the lexical meaning owner. self-reference alone does **not** remove a mentioned Topic target from the inventory **or** establish a new Topic target; a Term's spelling alone does **not** establish its Topic target. a source-admitted instance name after `//`, a selector literal, **or** syntax is **not** automatically a reusable Term. retain unresolved meaning as an explicit gap rather than treating it as ordinary wording.
2. select the **`=1`** canonical Topic target that the Claim governs **and** reference its narrowest exact Topic path directly through Main Subject.

   - for a Claim about entry **or** exit criteria of a Property, apply this same narrowest-target rule rather than substituting its wider bearer.
   - **when** the Atom has Content Role Evaluation **and** its Claim defines a conformance check, select the canonical target whose conformance is checked; do **not** select a generic Evaluation label **or** the execution of the check merely from its Content Role. bind the checked authority separately with `evaluation_for` under `CA-R-1018-CORE_META_MODEL-DECLARATION--register-evaluation-targets`.
3. connect **every** other Topic target **in** the mention inventory through Dependencies using its narrowest exact full Topic path. include mentions outside Claim; do **not** repeat Main Subject **or** add unmentioned Topic targets. unresolved mentions block completion rather than disappearing from the inventory.
4. for a definition Claim, use its defined Term **in** the Topic path that identifies the target being defined, under `CA-R-1279-CORE_META_MODEL-RULE--govern-every-defined-term`. resolve evidenced reusable lexical components through their Method Term Definitions, while resolving a name after `//` through its instance-naming and source authority rather than automatically requiring a Term Definition; the path identifies the target **and** Main Subject is the direct Topic reference. the path does **not** define its component Terms.
5. split the Atom **before** assignment **when** the Claim governs **`>1`** canonical Topic targets.
6. verify that the distinct Main Subject **and** Dependencies targets equal the mention inventory. record **every** reference once **without** creating an intermediate Topic object, repeating definitions, **or** treating path components **and** implicit bearer prefixes as separate Topic target mentions.
7. serialize the direct references under `CA-D-269-CORE_META_MODEL-ENG_DECISION--serialize-atom-subjects-in-frontmatter`. its migration-limited legacy compatibility preserves existing temporal carrier evidence; it does **not** add temporal nesting **to** a migrated flat Carrier.
