import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest


MODEL = Path(__file__).resolve().parents[2] / "TraceSemantics.lean"
EXAMPLES = """
namespace TraceSemantics
private def replyGuard : Guard :=
  ⟨.effect, "reply", some "model", some "received",
    [("current", .literal (.boolean true)), ("age", .atMost 3)], [], []⟩
private def displayGuard : Guard := ⟨.output, "display", some "ui", some\
 "ok", [], [], []⟩
private def reply : Event :=
  ⟨.effect, "reply", some "model", some "received",
    [("current", .boolean true), ("age", .integer 2)]⟩
private def display : Event := ⟨.output, "display", some "ui", some "ok", []⟩
private def replyEdge : Edge := ⟨"start", "ready", replyGuard⟩
private def displayEdge : Edge := ⟨"ready", "done", displayGuard⟩
private def sample : Workflow := ⟨"start", [replyEdge, displayEdge],\
 [("done", "ok")]⟩
private def wrongFirst : Edge := ⟨"start", "ready", displayGuard⟩
private def wrongReplyGuard : Guard := { replyGuard with kind := .output,\
 outcome := some "ok" }
private def wrongReply : Event := { reply with kind := .output, outcome :=\
 some "ok" }
private def wrongSecond : Edge := ⟨"ready", "done", wrongReplyGuard⟩
private def wrong : Workflow := ⟨"start", [wrongFirst, wrongSecond],\
 [("done", "ok")]⟩
private def okEdge : Edge := ⟨"start", "done", ⟨.output, "finish", none,\
 some "ok", [], [], []⟩⟩
private def errorEdge : Edge := ⟨"start", "done", ⟨.output, "finish", none,\
 some "error", [], [], []⟩⟩
private def sharedFinal : Workflow := ⟨"start", [okEdge, errorEdge],\
 [("done", "ok"), ("done", "error")]⟩
private def okEvent : Event := ⟨.output, "finish", none, some "ok", []⟩
private def errorEvent : Event := ⟨.output, "finish", none, some "error", []⟩
private def recordEdge : Edge := { replyEdge with guard := { replyGuard\
 with bind := [("age", "age")] } }
private def compareEdge : Edge := { displayEdge with guard := {\
 displayGuard with sameAs := [("id", "age")] } }
private def correlation : Workflow := ⟨"start", [recordEdge, compareEdge],\
 [("done", "ok")]⟩
private def correlated : Event := { display with detail := [("id", .integer\
 2)] }
private def stale : Event := { display with detail := [("id", .integer 3)] }

example : Runs correlation 2 "start" [reply, correlated] "ok" := by
  apply Runs.step (edge := recordEdge)
  · decide
  · rfl
  · decide
  · apply Runs.exit (edge := compareEdge) <;> decide
example : eventMatches compareEdge.guard correlated = false := by decide
example : eventMatches compareEdge.guard stale [("age", .integer 2)] =\
 false := by decide

example : eventMatches replyGuard reply = true := by decide
example : eventMatches { replyGuard with outcome := none } { reply with\
 outcome := none } = true := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean false), ("age", .integer 2)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .integer 1), ("age", .integer 2)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean true), ("age", .integer 4)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean true), ("age", .integer (-1))] } = false := by decide
example : check ⟨sample⟩ ⟨sample⟩ = true := by decide
example : check ⟨sample⟩ ⟨{ sample with edges := [displayEdge, replyEdge]\
 }⟩ = false := by decide
example : check ⟨sample⟩ ⟨{ sample with exits := [("done", "error")] }⟩ =\
 false := by decide
example : check ⟨sample⟩ ⟨wrong⟩ = false := by decide
example : Runs wrong 2 "start" [display, wrongReply] "ok" := by
  apply Runs.step (edge := wrongFirst)
  · decide
  · rfl
  · decide
  · apply Runs.exit (edge := wrongSecond)
    · decide
    · rfl
    · decide
    · rfl
    · rfl
    · decide
example : ¬ Runs sample 2 "start" [display, reply] "ok" := by
  intro run
  cases run with
  | step member origin matched _ =>
    simp only [sample, List.mem_cons, List.not_mem_nil, or_false] at member
    rcases member with same | same
    · subst same
      contradiction
    · subst same
      contradiction
example : Runs sample 2 "start" [reply, display] "ok" := by
  apply Runs.step (edge := replyEdge)
  · decide
  · rfl
  · decide
  · apply Runs.exit (edge := displayEdge)
    · decide
    · rfl
    · decide
    · rfl
    · rfl
    · decide

example : Runs sharedFinal 1 "start" [okEvent] "ok" := by
  apply Runs.exit (edge := okEdge) <;> decide
example : Runs sharedFinal 1 "start" [errorEvent] "error" := by
  apply Runs.exit (edge := errorEdge) <;> decide
example : eventMatches okEdge.guard { okEvent with outcome := none } =\
 false := by decide
example : ¬ Runs sharedFinal 0 "done" [] "ok" := by
  intro run
  cases run
example : ¬ Runs sharedFinal 1 "start" [okEvent] "error" := by
  intro run
  cases run with
  | exit member _ matched _ result _ =>
    simp only [sharedFinal, List.mem_cons, List.not_mem_nil, or_false] at\
 member
    rcases member with same | same <;> subst same <;> contradiction
  | step _ _ _ tail => cases tail
example : ¬ Runs sharedFinal 1 "start" [errorEvent] "ok" := by
  intro run
  cases run with
  | exit member _ matched _ result _ =>
    simp only [sharedFinal, List.mem_cons, List.not_mem_nil, or_false] at\
 member
    rcases member with same | same <;> subst same <;> contradiction
  | step _ _ _ tail => cases tail

#print axioms check_sound
#print axioms check_preserves_property
#print axioms check_preserves_order

end TraceSemantics
"""


class TraceSoundnessTests(unittest.TestCase):
    def test_typed_traces_and_axiom_audit(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "TraceSemanticsTest.lean"
            path.write_text(
                MODEL.read_text(encoding="utf-8") + EXAMPLES, encoding="utf-8"
            )
            result = subprocess.run(
                [lean, str(path)], capture_output=True, text=True, timeout=120
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            3, result.stdout.count("does not depend on any axioms")
        )
        self.assertNotIn("depends on axioms", result.stdout)
