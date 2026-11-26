import json

from .lean_values__pub import lean_string


def _details(detail):
    return '[' + ', '.join(
        f'({lean_string(json.dumps(key))}, {lean_string(json.dumps(value, separators=(",", ":")))})'
        for key, value in sorted(detail.items())) + ']'


def _effect(effect):
    return f'⟨{lean_string(effect[0])}, {lean_string(effect[1])}, {_details(effect[2] if len(effect) == 3 else {})}⟩'


def _effect_rules():
    return """def upperBound (value : String) : Option Nat := do
  let json ← (Lean.Json.parse value).toOption
  let .obj entries := json | none
  if entries.foldl (init := 0) (fun n _ _ => n + 1) != 1 then none else do
    let bound ← (json.getObjVal? "at_most").toOption
    bound.getNat?.toOption
def detailImplies (actual required : String) : Bool :=
  if actual == required then true else
  match upperBound required with
  | none => false
  | some bound =>
    let actualBound := upperBound actual <|> ((Lean.Json.parse actual).toOption >>= fun json => json.getNat?.toOption)
    actualBound.any (fun n => n <= bound)
structure Effect where
  observed : String
  outcome : String
  detail : List (String × String)
def implies (actual required : Effect) : Bool :=
  actual.observed == required.observed && actual.outcome == required.outcome &&
  required.detail.all (fun pair => actual.detail.any (fun found => found.1 == pair.1 && detailImplies found.2 pair.2))
"""


def _edges(states):
    final = {state['name'] for state in states if state['final']}
    edges = []
    for state in states:
        for transition in state['transitions']:
            expect = transition['expect']
            values = (state['name'], transition['target'], expect['kind'],
                      expect.get('target') or '', expect.get('outcome') or '')
            flags = ('outcome' not in expect, transition['target'] in final, 'target' not in expect,
                     not (expect.get('outcome') or '').strip())
            fields = [*(lean_string(value) for value in values), *(str(flag).lower() for flag in flags),
                      _details(expect.get('detail') or {}), lean_string(transition['event'])]
            edges.append('⟨' + ', '.join(fields) + '⟩')
    return ', '.join(edges)


def _rules(count):
    return f'''def selected (e : Edge) : Bool := e.kind == "output" && e.final && (e.wildcard || e.outcome == output)
def reachable (start : String) (removed : Option Effect) : List String :=
  (List.range {count}).foldl (fun reached _ =>
    edges.foldl (fun seen e =>
      if seen.contains e.source && !(removed.any (fun r => e.kind == "effect" && implies ⟨e.observed, e.outcome, e.detail⟩ r))
      then if seen.contains e.target then seen else e.target :: seen else seen) reached) [start]
def effectStatus (effect : Effect) : String :=
  let reached := reachable initial (some effect)
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e => selected e && reached.contains e.source)
       then "conflicting" else "matched"
def forbiddenStatus (target : String) : String :=
  let reached := reachable initial none
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e =>
       let after := reachable e.target none
       e.kind == "effect" && (e.targetWildcard || e.observed == target) && reached.contains e.source &&
       edges.any (fun terminal => selected terminal && after.contains terminal.source))
       then "conflicting" else "matched"
def orderStatus (order : Effect × Effect) : String :=
  let reached := reachable initial (some order.1)
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e =>
       let after := reachable e.target none
       e.kind == "effect" && (e.targetWildcard || e.observed == order.2.observed) &&
       (e.wildcard || e.outcome == order.2.outcome) &&
       order.2.detail.all (fun pair => !(e.detail.any (fun found => found.1 == pair.1)) ||
         e.detail.any (fun found => found.1 == pair.1 &&
           (detailImplies found.2 pair.2 || detailImplies pair.2 found.2))) && reached.contains e.source &&
       edges.any (fun terminal => selected terminal && after.contains terminal.source))
       then "conflicting" else "matched"
'''


def _program(contract, workflow):
    states = workflow['states']
    effects = ', '.join(_effect(effect) for effect in contract.get('must_effect', []))
    forbidden = ', '.join(lean_string(target) for target in contract.get('forbid_effect', []))
    orders = ', '.join(f'({_effect(before)}, {_effect(after)})'
                       for before, after in contract.get('must_precede', []))
    return f'''import Lean
{_effect_rules()}structure Edge where
  source : String
  target : String
  kind : String
  observed : String
  outcome : String
  wildcard : Bool
  final : Bool
  targetWildcard : Bool
  missingOutcome : Bool
  detail : List (String × String)
  event : String

def edges : List Edge := [{_edges(states)}]
def initial : String := {lean_string(workflow['initial'])}
def output : String := {lean_string(contract['output'])}
def effects : List Effect := [{effects}]
def forbidden : List String := [{forbidden}]
def orders : List (Effect × Effect) := [{orders}]
{_rules(len(states))}def terminalStatus : String :=
  let reached := reachable initial none
  if {str(any(state['final'] and state['name'] == workflow['initial'] for state in states)).lower()} ||
     edges.any (fun e => e.final && reached.contains e.source && e.kind != "output") then "conflicting"
  else if edges.any (fun e => e.final && reached.contains e.source && e.missingOutcome) then "unresolved"
  else if edges.any (fun e => e.final && reached.contains e.source) then "matched" else "unresolved"
def actionStatus : String :=
  if {lean_string(contract['action'])} == {lean_string(workflow['action'])} then "matched" else "conflicting"
#eval IO.println (Lean.toJson (actionStatus :: effects.map effectStatus ++ forbidden.map forbiddenStatus ++ orders.map orderStatus ++ [terminalStatus])).compress
'''
