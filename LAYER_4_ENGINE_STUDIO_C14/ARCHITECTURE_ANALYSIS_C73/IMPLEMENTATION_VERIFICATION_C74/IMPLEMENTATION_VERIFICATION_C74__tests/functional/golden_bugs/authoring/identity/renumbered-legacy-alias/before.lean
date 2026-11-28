-- valid abstracts the regex fullmatch result. Versions are the strings after
-- the source rsplit and removesuffix operations.
-- Prior path checks have passed.
def reject (valid seen : Bool) (oldVersion targetVersion : String) : Bool :=
  (!valid) || seen || (oldVersion != targetVersion)

example : reject true false "1" "2" = true := rfl
