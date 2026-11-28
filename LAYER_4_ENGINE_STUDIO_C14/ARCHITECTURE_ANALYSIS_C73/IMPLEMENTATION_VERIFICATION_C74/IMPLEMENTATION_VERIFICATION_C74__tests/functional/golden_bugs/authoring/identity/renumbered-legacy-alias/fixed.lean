-- valid abstracts the regex fullmatch result. Versions are the strings after
-- the source rsplit and removesuffix operations.
-- Prior path checks have passed.
def reject (valid seen : Bool) (_oldVersion _targetVersion : String) : Bool :=
  (!valid) || seen

theorem accepts_valid_unique (oldVersion targetVersion : String) :
  reject true false oldVersion targetVersion = false := rfl
example : reject true false "1" "2" = false := rfl
example : reject true true "1" "2" = true := rfl
