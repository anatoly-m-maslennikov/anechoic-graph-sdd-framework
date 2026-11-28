import Lean
-- Frozen projections of the admitted historical AST shapes.
namespace Before
set_option linter.unusedVariables false
inductive Outcome where
  | failed
  | indexed (summary : String) (markdown : String)
  deriving BEq, Repr, DecidableEq
-- The row has valid references and two already parsed Summary spans.
def implementation (first second markdown : String) : Outcome :=
  match none with
  | none => .failed
  | some value => .indexed value markdown
-- Independent requirement: retain the first value and original Markdown.
def specification (first second markdown : String) : Outcome :=
  .indexed first markdown
example : implementation "first" "second" "## Summary\nfirst\n## Summary\nsecond\n" ≠
    specification "first" "second" "## Summary\nfirst\n## Summary\nsecond\n" := by decide
end Before
namespace Fixed
set_option linter.unusedVariables false
inductive Outcome where
  | failed
  | indexed (summary : String) (markdown : String)
  deriving BEq, Repr, DecidableEq
-- The row has valid references and two already parsed Summary spans.
def implementation (first second markdown : String) : Outcome :=
  match some first with
  | none => .failed
  | some value => .indexed value markdown
-- Independent requirement: retain the first value and original Markdown.
def specification (first second markdown : String) : Outcome :=
  .indexed first markdown
example : implementation "first" "second" "## Summary\nfirst\n## Summary\nsecond\n" =
    specification "first" "second" "## Summary\nfirst\n## Summary\nsecond\n" := by decide
end Fixed
#eval IO.println "first-summary-survives-duplicate: old mismatch; fixed matches"
