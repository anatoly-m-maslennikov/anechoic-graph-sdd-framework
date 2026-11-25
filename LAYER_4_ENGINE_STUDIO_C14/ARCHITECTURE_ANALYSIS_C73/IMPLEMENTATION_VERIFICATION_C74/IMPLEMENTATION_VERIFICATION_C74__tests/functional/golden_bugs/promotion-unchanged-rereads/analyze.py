#!/usr/bin/env -S python3 -B
"""Project a historical promotion read-count path into Lean; unknown shapes are unresolved."""
import argparse, ast, json, pathlib, subprocess, tempfile

p=argparse.ArgumentParser(); p.add_argument('checkout',type=pathlib.Path); p.add_argument('--lean',required=True); a=p.parse_args()
base=a.checkout/'LAYER_3_ENGINE_STUDIO_C14'; draft=base/'FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/native_draft.py'; source=base/'IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/native_source_rows.py'
result={'findings':[],'unresolved':[]}
def fn(tree,name): return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
def assignments(node,name): return [x for x in ast.walk(node) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets)]
def has(node,text): return any(ast.unparse(x)==text for x in ast.walk(node))
try:
 t=ast.parse(draft.read_text()); s=ast.parse(source.read_text()); promotion=fn(t,'promote_draft'); capture=fn(s,'capture_native')
 call=assignments(promotion,'capture'); assert len(call)==1
 expr=ast.unparse(call[0].value)
 assert has(capture,'reader.inventory(control)') and has(capture,'reader.read(path, metadata_guard=incremental, skip_version=versions.get(str(path)) if incremental else None)')
 if expr=='capture_native(selection)':
  projected='population'; method='full capture'
 elif expr=='revalidate_native(selection, previous_capture)':
  revalidate=fn(s,'revalidate_native'); changed=fn(s,'_changed_inputs')
  assert has(revalidate,'capture_native(selection, previous=previous, paths=changed)')
  assert has(revalidate,'previous is None or previous.errors')
  assert has(revalidate,'before.get(path) != previous.versions.get(path)')
  assert has(capture,'previous is not None and paths is not None')
  assert has(capture,'_changed_inputs(reader, root, control, previous, paths)')
  assert has(changed,'[root / path for path in sorted(changed - directories)]')
  assert any(isinstance(x,ast.Assign) and ast.unparse(x) == 'changed, directories = (set(), set())' for x in changed.body)
  loops=[x for x in changed.body if isinstance(x,ast.For) and ast.unparse(x.iter)=='scopes']
  assert len(loops)==1
  updates=[x for x in ast.walk(changed) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='changed']
  assert updates and all(x in set(ast.walk(loops[0])) for x in updates)
  projected='changed'; method='metadata revalidation with changed paths'
 else: raise ValueError('unrecognized promotion capture: '+expr)
 lean=f'''set_option linter.unusedVariables false\n-- AST projection: population means all carriers, changed means selected changed paths.\ndef reads (population changed : Nat) : Nat := {projected}\n-- Independent invariant: with a valid prior capture and unchanged metadata, no carrier body is reread.\n#eval reads 3 0 == 0\n-- Control: a changed carrier remains eligible for reading.\n#eval reads 3 1 > 0\n'''
 with tempfile.TemporaryDirectory() as d:
  path=pathlib.Path(d)/'Check.lean'; path.write_text(lean); run=subprocess.run([a.lean,str(path)],text=True,capture_output=True,timeout=30)
 if run.returncode or run.stdout.split()!=['true','true'] and run.stdout.split()!=['false','true']: raise ValueError('Lean failed or unexpected output: '+run.stdout+run.stderr)
 if run.stdout.split()[0]=='false': result['findings'].append({'path':str(draft.relative_to(a.checkout)),'detail':'Promotion full capture rereads unchanged carrier bodies (Lean counterexample: 3 carriers, 0 changed).','projection':method})
except (OSError,ValueError,StopIteration,AssertionError,subprocess.SubprocessError,SyntaxError) as e: result['unresolved'].append(str(e) or 'unrecognized source shape')
print(json.dumps(result))
