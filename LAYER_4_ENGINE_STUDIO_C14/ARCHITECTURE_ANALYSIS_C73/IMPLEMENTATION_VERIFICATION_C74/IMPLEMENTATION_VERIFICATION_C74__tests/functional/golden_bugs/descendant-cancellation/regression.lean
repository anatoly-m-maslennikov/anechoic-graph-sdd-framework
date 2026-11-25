-- Reference controls; checkout analysis generates its own Lean source.
example : (true && !(false && true)) = true := by decide
example : (!(true && (!(true) || !(true)))) = true := by decide
example : (true && !false) = true := by decide
