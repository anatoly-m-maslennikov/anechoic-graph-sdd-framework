-- Python guard precondition: status is a nonempty string;
-- no Ref ID was supplied.
-- derive represents the helper embedded in the source fixture.
structure State where
  atom_id : String
  version : Nat
  status : String

-- The generated __post_init__ stores this result once.
def init (derive : String → Nat → String → String) (s : State) : String :=
  derive s.atom_id s.version s.status
def read (stored : String) (_s : State) : String := stored

-- On this valid active-status slice the historical helper
-- formats this reference.
def deriveActive (id : String) (version : Nat) (_status : String) : String :=
  id ++ "@" ++ toString version
def beforeState : State := ⟨"AN-S-1", 1, "active"⟩
def afterState : State := ⟨"AN-S-1", 2, "active"⟩
example : read (init deriveActive beforeState) afterState ≠
    deriveActive afterState.atom_id afterState.version afterState.status := by
  decide
