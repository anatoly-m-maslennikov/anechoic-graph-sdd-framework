import Lean

namespace TraceSemantics

inductive Literal where
  | null
  | boolean (value : Bool)
  | integer (value : Int)
  | text (value : String)
  deriving DecidableEq, Repr

inductive DetailGuard where
  | literal (value : Literal)
  | atMost (bound : Nat)
  deriving DecidableEq, Repr

inductive Kind where
  | trigger | effect | output
  deriving DecidableEq, Repr

structure Event where
  kind : Kind
  name : String
  target : Option String
  outcome : Option String
  detail : List (String × Literal)
  deriving DecidableEq, Repr

structure Guard where
  kind : Kind
  name : String
  target : Option String
  outcome : Option String
  detail : List (String × DetailGuard)
  bind : List (String × String)
  sameAs : List (String × String)
  deriving DecidableEq, Repr

structure Edge where
  source : String
  target : String
  guard : Guard
  deriving DecidableEq, Repr

structure Workflow where
  initial : String
  edges : List Edge
  exits : List (String × String)
  deriving DecidableEq, Repr

structure SourceWorkflow where
  model : Workflow
  deriving DecidableEq, Repr

structure TargetWorkflow where
  model : Workflow
  deriving DecidableEq, Repr

def detailMatches (guard : DetailGuard) (actual : Literal) : Bool :=
  match guard with
  | .literal expected => decide (expected = actual)
  | .atMost bound =>
    match actual with
    | .integer value =>
      match value with
      | .ofNat n => n <= bound
      | .negSucc _ => false
    | .null => false
    | .boolean _ => false
    | .text _ => false

abbrev Bindings := List (String × Literal)

def bindDetail (guard : Guard) (event : Event) (bindings : Bindings) :
    Option Bindings := do
  guard.bind.foldlM (fun updated (alias, key) => do
    let value ← event.detail.lookup key
    match updated.lookup alias with
    | none => some ((alias, value) :: updated)
    | some prior => if value == prior then some updated else none) bindings

def eventMatches (guard : Guard) (event : Event) (bindings : Bindings := [])
  : Bool :=
  decide (guard.kind = event.kind ∧ guard.name = event.name) &&
  guard.target.all (fun value => event.target == some value) &&
  guard.outcome.all (fun value => event.outcome == some value) &&
  guard.detail.all (fun (key, expected) =>
    event.detail.any (fun (actualKey, value) =>
      actualKey == key && detailMatches expected value)) &&
  guard.sameAs.all (fun (key, alias) =>
    (bindings.lookup alias).any (fun prior => event.detail.lookup key == some
      prior)) &&
  (bindDetail guard event bindings).isSome

abbrev Trace := List Event × String

inductive Runs (workflow : Workflow) : Nat → String → List Event → String →
  (_ : Bindings := []) → Prop where
  | exit {bound state event outcome edge bindings} :
      edge ∈ workflow.edges → edge.source = state → eventMatches edge.guard
        event bindings = true →
      edge.guard.kind = .output → edge.guard.outcome = some outcome →
      (edge.target, outcome) ∈ workflow.exits →
      Runs workflow (bound + 1) state [event] outcome bindings
  | step {bound state event rest outcome edge bindings} :
      edge ∈ workflow.edges → edge.source = state → eventMatches edge.guard
        event bindings = true →
      Runs workflow bound edge.target rest outcome ((bindDetail edge.guard
        event bindings).getD []) →
      Runs workflow (bound + 1) state (event :: rest) outcome bindings

def sourceTrace (source : SourceWorkflow) (bound : Nat) (trace : Trace) :
  Prop :=
  Runs source.model bound source.model.initial trace.1 trace.2

def targetTrace (target : TargetWorkflow) (bound : Nat) (trace : Trace) :
  Prop :=
  Runs target.model bound target.model.initial trace.1 trace.2

def check (source : SourceWorkflow) (target : TargetWorkflow) : Bool :=
  decide (source.model = target.model)

theorem check_sound (source : SourceWorkflow) (target : TargetWorkflow)
    (accepted : check source target = true) (bound : Nat) (trace : Trace) :
    sourceTrace source bound trace ↔ targetTrace target bound trace := by
  cases source with
  | mk sourceModel =>
    cases target with
    | mk targetModel =>
      have same : sourceModel = targetModel := of_decide_eq_true accepted
      cases same
      rfl

def precedes (before after : Event) (trace : Trace) : Prop :=
  ∀ prior later, trace.1 = prior ++ [after] ++ later → before ∈ prior

theorem check_preserves_property (source : SourceWorkflow)
    (target : TargetWorkflow)
    (accepted : check source target = true) (bound : Nat)
    (property : Trace → Prop) :
    (∀ trace, sourceTrace source bound trace → property trace) ↔
    (∀ trace, targetTrace target bound trace → property trace) := by
  constructor <;> intro h trace run
  · exact h trace ((check_sound source target accepted bound trace).2 run)
  · exact h trace ((check_sound source target accepted bound trace).1 run)

theorem check_preserves_order (source : SourceWorkflow)
    (target : TargetWorkflow)
    (accepted : check source target = true) (bound : Nat)
    (before after : Event) :
    (∀ trace, sourceTrace source bound trace → precedes before after trace) ↔
    (∀ trace, targetTrace target bound trace → precedes before after trace) :=
  check_preserves_property source target accepted bound (precedes before after)

end TraceSemantics
