-- Abstract the Python start() scheduling decision for one top-level directory.
-- rootRecursive models the recursive argument passed to observer.schedule(root).
-- childRecursive models the additional schedule for an eligible child.
def oldRootRecursive : Bool := true
def fixedRootRecursive (hasFilter : Bool) : Bool := !hasFilter
def fixedChildRecursive (hasFilter isDir isSymlink excluded : Bool) : Bool :=
  hasFilter && isDir && !isSymlink && !excluded
-- Independent invariant: an excluded top-level directory must not be covered
-- by either the recursive root watch or its own recursive child watch.
def covered (rootRecursive childRecursive : Bool) : Bool := rootRecursive || childRecursive

theorem old_counterexample : covered oldRootRecursive false = true := by decide

theorem fixed_excluded (isDir isSymlink : Bool) :
    covered (fixedRootRecursive true) (fixedChildRecursive true isDir isSymlink true) = false := by
  cases isDir <;> cases isSymlink <;> decide

theorem fixed_included :
    covered (fixedRootRecursive true) (fixedChildRecursive true true false false) = true := by decide
