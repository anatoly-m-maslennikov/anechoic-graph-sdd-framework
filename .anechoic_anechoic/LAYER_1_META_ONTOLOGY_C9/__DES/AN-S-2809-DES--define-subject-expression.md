---
atom_family: SPEC
atom_id: AN-S-2809
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 37
  updated_at: '2026-11-13T23:01:25.455940+00:00'
---
## Summary

Define Subject Expression

## Claim

### Prose Claim


Subject Expressions formed from entity names, reusable Term components, and registered relation syntax.




The following interpretation is required when this governed concept is used:

a Subject Expression **means** a reference **to** **`=1`** canonical Subject Target formed from entity names and registered relation syntax. A qualified Atom expression uses the admitted Role and Form Properties, for example `Atom/(.Header.Role := Plan)/(.Header.Form := Epic)` when both values are admitted.

Outside the Term branch, an Entity reference **must** use its exact complete canonical expression with every source-established qualifier; a bare Term is not that expression. The sole one-Term exception is the Subject root `Entity`. Ordinary lexical components **may** reuse Terms with consistent approved meanings; an instance's name is **not** automatically a lexical Term. Inside `((...))`, a registered direct Relation token resolves to **`=1`** admitted Relation Type under the named-Relation notation. Its bare spelling is not that Relation Type entity's complete canonical expression; naming comparison uses the full qualified expression separately. A qualified Atom expression such as `Atom/(.Header.Role := <exact Role>)/(.Header.Form := <exact Form>)` is available only when both exact values have independent source admission; its segments do not become admitted merely by appearing in an expression.

### Subject notation

- In MODEL, `X//Y` identifies Y as a narrower declared kind of X. `X.p` selects a Property of X, including an inherited Property through its existing Declaration.
- In STRUCTURE, `Whole/Part` identifies Part through immediate containment. Chaining paths follows each declared container in order. For example, `ANECHOIC_STRUCTURE/FRAMEWORK_ENGINE/PROGRAMMATIC` identifies the PROGRAMMATIC Scope Unit.
- A qualified kind selects the scope where its Property has an admitted value. Existing Subject addresses retain their resolved targets during the notation migration.
- `X >| Axis` and `Axis |< X` express classification. Relation Declarations identify canonical Relations and their inverse aliases.
- `Source ((RELATION)) Target` and `Target <((RELATION)) Source` write the same fact. Reverse writing swaps the endpoints and their count slots. Endpoint permissions come from the Relation and applicable Entity Declarations.
- Parentheses group expressions. Where a Subject admits Property selectors, `X.*` selects immediate dependents and `X.**` selects all descendants. A format in square brackets applies to values. A cardinality belongs to its written Property or Relation endpoint. Use the Subject parser's admitted count syntax `{n}`, `{n+}` or `{n..m}`.
- Quote a value when punctuation would otherwise be parsed as notation. For example, `"A/B"` is one literal value. Names with reserved characters use the reserved-separator rules in CA-R-1324. Atom Ref IDs retain their own version syntax.

CA-R-1931 supplies complementary separator rules. Subject notation identifies declared targets; the declarations supply their meaning and constraints.

The complete expression **must** resolve **to** **`=1`** canonical Subject Target that already exists **or** is explicitly introduced by applicable defining authority under CA-R-1194 **and** CA-R-1931. Syntax alone neither creates **nor** admits a target **or** native EntityGraph fact. The expression identifies the target, **not** the Atom's Subject Relation **to** it. An arbitrary composite expression is **not** one Term **or** automatically one entity name; an admitted qualified property name **may** identify **`=1`** entity.

## Details

Subjects do not carry Atom or Artifact IDs, whether bare, version-qualified, or embedded in an ID selector. Use typed Relations for links to those Atoms or Artifacts. The contextual topic/code spellings `atom.id` and `projection.id` distinguish their respective ID Properties, not particular identifier values. They are not alternative complete canonical Subject names or case-folded aliases; an authored Subject uses its full admitted expression. Their shared terminal label and reusable `ID` meaning do not collide. Dot remains an operator; these contextual spellings are not renamed to `atom.atom_id` or another invented spelling. Named-instance Subjects use names, not IDs. Source/provenance metadata outside Subjects is not prohibited.

An object has its containment address in STRUCTURE. Each step follows one
declared `IS_CONTAINED_BY` fact from Container to Part. A complete path
preserves the object's identity even when a local name occurs elsewhere.
Older named-instance Topic selectors remain readable during migration.

`Entity/Object/Continuant/Package`, `Entity/Object/Continuant/Package <+ Module`, and `Entity/Object/Continuant/Package <+ Module <+ Code Unit` identify three connected entities. The chain is not one Term or a fourth entity. `Package`, `Module`, and `Code Unit` are their reusable lexical components, not their complete Entity expressions. Likewise, `Package` and `Unit` are reusable Terms whose occurrence does not itself introduce an entity or Relation. The rule applies to exact full expressions in authored prose as well as Subjects. Literal source quotations and code identifiers remain distinguishable and are not automatically renamed. Arbitrary instance names and identifiers outside this modeled-entity naming role are not automatically lexical definitions.

Entity is the canonical expression root under CA-R-1194. The registered operators retain their meanings and native-fact admission boundaries. No new alias, parser, resolver grammar, formula, or unadopted syntax is introduced by this definition.
