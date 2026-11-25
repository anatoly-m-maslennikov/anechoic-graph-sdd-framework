import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest


MODEL = Path(__file__).resolve().parents[2] / 'TraceSemantics.lean'
EXAMPLES = r'''
namespace TraceSemantics
private def replyGuard : Guard :=
  ⟨.effect, "reply", some "model", some "received",
    [("current", .literal (.boolean true)), ("age", .atMost 3)]⟩
private def displayGuard : Guard := ⟨.effect, "display", some "ui", some "shown", []⟩
private def reply : Event :=
  ⟨.effect, "reply", some "model", some "received",
    [("current", .boolean true), ("age", .integer 2)]⟩
private def display : Event := ⟨.effect, "display", some "ui", some "shown", []⟩
private def replyEdge : Edge := ⟨"start", "ready", replyGuard⟩
private def displayEdge : Edge := ⟨"ready", "done", displayGuard⟩
private def sample : Workflow := ⟨"start", [replyEdge, displayEdge], [("done", "ok")]⟩
private def wrongFirst : Edge := ⟨"start", "ready", displayGuard⟩
private def wrongSecond : Edge := ⟨"ready", "done", replyGuard⟩
private def wrong : Workflow := ⟨"start", [wrongFirst, wrongSecond], [("done", "ok")]⟩

example : eventMatches replyGuard reply = true := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean false), ("age", .integer 2)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .integer 1), ("age", .integer 2)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean true), ("age", .integer 4)] } = false := by decide
example : eventMatches replyGuard { reply with detail :=
    [("current", .boolean true), ("age", .integer (-1))] } = false := by decide
example : check ⟨sample⟩ ⟨sample⟩ = true := by decide
example : check ⟨sample⟩ ⟨{ sample with edges := [displayEdge, replyEdge] }⟩ = false := by decide
example : check ⟨sample⟩ ⟨{ sample with exits := [("done", "error")] }⟩ = false := by decide
example : check ⟨sample⟩ ⟨wrong⟩ = false := by decide
example : Runs wrong 2 "start" [display, reply] "ok" := by
  apply Runs.step (edge := wrongFirst)
  · decide
  · rfl
  · decide
  · apply Runs.step (edge := wrongSecond)
    · decide
    · rfl
    · decide
    · apply Runs.exit
      decide
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
  · apply Runs.step (edge := displayEdge)
    · decide
    · rfl
    · decide
    · apply Runs.exit
      decide

#print axioms check_sound
#print axioms check_preserves_property
#print axioms check_preserves_order

end TraceSemantics
'''


class TraceSoundnessTests(unittest.TestCase):
    def test_typed_traces_and_axiom_audit(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'TraceSemanticsTest.lean'
            path.write_text(MODEL.read_text(encoding='utf-8') + EXAMPLES, encoding='utf-8')
            result = subprocess.run([lean, str(path)], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(3, result.stdout.count('does not depend on any axioms'))
        self.assertNotIn('depends on axioms', result.stdout)
