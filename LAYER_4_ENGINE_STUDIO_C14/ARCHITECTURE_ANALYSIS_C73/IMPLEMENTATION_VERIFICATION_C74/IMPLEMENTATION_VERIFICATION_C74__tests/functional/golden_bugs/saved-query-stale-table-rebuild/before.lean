inductive Event where
  | materialize | drop | bind
  deriving Repr

def readsFresh : List Event → Bool → Bool → Bool
  | [], _, _ => false
  | .materialize :: rest, fresh, false => readsFresh rest fresh true
  | .materialize :: _, fresh, true => fresh
  | .drop :: rest, _, seen => readsFresh rest false seen
  | .bind :: rest, _, seen => readsFresh rest true seen
def extractedEvents : List Event := [.materialize, .materialize, .drop, .drop]
#eval readsFresh extractedEvents false false
