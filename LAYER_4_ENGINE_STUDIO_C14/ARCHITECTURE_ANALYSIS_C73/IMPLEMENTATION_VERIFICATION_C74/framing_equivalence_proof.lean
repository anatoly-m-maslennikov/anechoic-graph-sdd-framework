namespace C30FramingEquivalence

set_option maxHeartbeats 800000

theorem opening_eq (raw : List Nat) :
    CarrierBodyContract.openingEnd raw = CarrierBodySolution.opening raw := by
  unfold CarrierBodyContract.openingEnd CarrierBodySolution.opening
  by_cases a : raw.take 5 = [45,45,45,13,10]
  · have b : raw.take 4 = [45,45,45,13] := by
      have h := congrArg (List.take 4) a
      simpa [List.take_take] using h
    simp [a, b]
  · simp [a]

private theorem bind_if (c : Prop) [Decidable c] (s t : Option α) (f : α → Option β) :
    (if c then s else t).bind f = (if c then s.bind f else t.bind f) := by split <;> rfl

theorem closing_eq (raw : List Nat) (p : Nat) :
    CarrierBodyContract.closingEnd raw p =
      (CarrierBodySolution.closingLength (raw.drop p)).map (p + ·) := by
  unfold CarrierBodyContract.closingEnd
  simp only [← List.drop_drop]
  generalize raw.drop p = xs
  rcases xs with _ | ⟨a, _ | ⟨b, _ | ⟨c, _ | ⟨d, _ | ⟨e, _ | ⟨f, _ | ⟨g, xs⟩⟩⟩⟩⟩⟩⟩
  all_goals simp [CarrierBodyContract.lineEndLength, CarrierBodySolution.closingLength,
    bind_if, List.take, List.drop, Nat.add_assoc]
  all_goals grind (splits := 24)

private theorem scan_eq
    (raw suffix : List Nat) (p : Nat) (h : raw.drop p = suffix) :
    (do
      let start ← (List.range' p suffix.length).find? (fun i => (CarrierBodyContract.closingEnd raw i).isSome)
      let stop ← CarrierBodyContract.closingEnd raw start
      some (start, stop)) = CarrierBodySolution.firstClosing suffix p := by
  induction suffix generalizing p with
  | nil => rfl
  | cons a tail ih =>
    have htail : raw.drop (p + 1) = tail := by rw [← List.drop_drop, h]; rfl
    have hclose := closing_eq raw p
    rw [h] at hclose
    simp only [List.length_cons, List.range'_succ, List.find?_cons, CarrierBodySolution.firstClosing]
    cases hs : CarrierBodySolution.closingLength (a :: tail) with
    | none =>
      simp [hs] at hclose
      simpa [hclose] using ih (p + 1) htail
    | some n =>
      simp [hs] at hclose
      simp [hclose]

theorem bounds_eq
    (raw : List Nat) : CarrierBodyContract.bounds raw = CarrierBodySolution.bounds raw := by
  unfold CarrierBodyContract.bounds CarrierBodySolution.bounds
  rw [opening_eq]
  cases CarrierBodySolution.opening raw with
  | none => rfl
  | some n =>
    simp only [Option.bind_eq_bind, Option.bind_some]
    have scan := scan_eq raw (raw.drop (n - 1)) (n - 1) rfl
    rw [← scan]
    simp only [List.range_eq_range', List.drop_range', Nat.mul_one, Nat.zero_add, List.length_drop]
    cases (List.range' (n - 1) (raw.length - (n - 1))).find?
      (fun i => (CarrierBodyContract.closingEnd raw i).isSome) with
    | none => rfl
    | some s =>
      simp only [Option.bind_eq_bind, Option.bind_some]
      cases CarrierBodyContract.closingEnd raw s <;> rfl

theorem body_eq (raw : List Nat) :
    CarrierBodyContract.body raw =
      (match CarrierBodySolution.body raw with
       | .missingDelimiter => .missingDelimiter
       | .body bytes => .body bytes) := by
  unfold CarrierBodyContract.body CarrierBodySolution.body
  rw [bounds_eq]
  cases CarrierBodySolution.bounds raw <;> rfl

end C30FramingEquivalence

namespace C30ImplementationEquivalence

private theorem closing_eq (raw : List Nat) :
    closingLength raw = CarrierBodySolution.closingLength raw := by
  unfold closingLength closingPatterns CarrierBodySolution.closingLength
  simp [List.find?]
  repeat' (split <;> simp_all)

private theorem search_eq (suffix : List Nat) (p : Nat) :
    findClosing suffix p = CarrierBodySolution.firstClosing suffix p := by
  induction suffix generalizing p with
  | nil => rfl
  | cons a tail ih =>
    simp only [findClosing, CarrierBodySolution.firstClosing, closing_eq]
    cases CarrierBodySolution.closingLength (a :: tail) with
    | none => exact ih (p + 1)
    | some => rfl

theorem solution_bounds (raw : List Nat) :
    frontmatterBounds raw = CarrierBodySolution.bounds raw := by
  unfold frontmatterBounds CarrierBodySolution.bounds CarrierBodySolution.opening
  by_cases a : raw.take 4 = [45,45,45,10] <;>
    by_cases b : raw.take 5 = [45,45,45,13,10] <;>
    simp [openingLF, openingCRLF, search_eq, a, b]

theorem manifest_bounds (raw : List Nat) :
    frontmatterBounds raw = CarrierBodyContract.bounds raw :=
  (solution_bounds raw).trans (C30FramingEquivalence.bounds_eq raw).symm

theorem solution_body (raw : List Nat) (path : String) :
    sourceBody raw path =
      (match CarrierBodySolution.body raw with
       | .missingDelimiter => .error (path ++ ": unsupported frontmatter delimiter")
       | .body bytes => .ok bytes) := by
  unfold sourceBody CarrierBodySolution.body
  rw [solution_bounds]
  cases CarrierBodySolution.bounds raw <;> rfl

theorem manifest_body (raw : List Nat) (path : String) :
    sourceBody raw path =
      (match CarrierBodyContract.body raw with
       | .missingDelimiter => .error (path ++ ": unsupported frontmatter delimiter")
       | .body bytes => .ok bytes) := by
  unfold sourceBody CarrierBodyContract.body
  rw [manifest_bounds]
  cases CarrierBodyContract.bounds raw <;> rfl

end C30ImplementationEquivalence
