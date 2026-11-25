-- Python guard precondition: status is a nonempty string; no Ref ID was supplied.
-- derive represents the helper embedded in the source fixture.
structure State where
  atom_id : String
  version : Nat
  status : String

-- The generated property calls the helper for every read.
def read (derive : String → Nat → String → String) (s : State) : String :=
  derive s.atom_id s.version s.status

theorem read_follows_state (derive : String → Nat → String → String) (s : State) :
  read derive s = derive s.atom_id s.version s.status := rfl
