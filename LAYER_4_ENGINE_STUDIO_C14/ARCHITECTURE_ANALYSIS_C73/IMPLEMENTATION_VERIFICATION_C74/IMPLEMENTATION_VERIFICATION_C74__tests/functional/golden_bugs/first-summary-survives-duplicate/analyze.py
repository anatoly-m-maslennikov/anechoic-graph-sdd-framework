"""Check the admitted native snapshot Summary projections in a source checkout."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def functions(tree):
    result = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in result:
                raise ValueError('duplicate function ' + node.name)
            result[node.name] = node
    return result


def shape(node):
    return ast.dump(node, include_attributes=False)


def discover(checkout):
    found = []
    for path in checkout.rglob('native_generation_snapshot.py'):
        if '.git' in path.parts:
            continue
        tree = ast.parse(path.read_bytes(), filename=str(path))
        names = functions(tree)
        if {'_atoms', 'snapshot'} <= names.keys():
            found.append((path, tree, names))
    if len(found) != 1:
        raise ValueError(f'expected one native snapshot implementation, found {len(found)}')
    return found[0]


def bind(checkout):
    path, tree, names = discover(checkout)
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and
               n.level == 1 and n.module == 'markdown_content__pub' and
               [(a.name, a.asname) for a in n.names] == [('content_lines', None)]]
    if len(imports) != 1:
        raise ValueError('unsupported content_lines binding')
    markdown = path.with_name('markdown_content__pub.py')
    md_names = functions(ast.parse(markdown.read_bytes(), filename=str(markdown)))
    if 'content_lines' not in md_names:
        raise ValueError('missing content_lines')
    for tag in ('before', 'fixed'):
        reference = functions(ast.parse((HERE / (tag + '.py.txt')).read_bytes()))
        md_reference = functions(ast.parse((HERE / (tag + '-markdown.py.txt')).read_bytes()))
        required = ['_atoms', 'snapshot'] + (['row_summary'] if tag == 'fixed' else [])
        if (all(name in names and shape(names[name]) == shape(reference[name]) for name in required)
                and shape(md_names['content_lines']) == shape(md_reference['content_lines'])
                and (tag != 'before' or 'row_summary' not in names)):
            return tag, path, markdown
    raise ValueError('unsupported snapshot or content_lines AST')


def lean_model(tag):
    selected = 'none' if tag == 'before' else 'some first'
    return '''import Lean
set_option linter.unusedVariables false
inductive Outcome where
  | failed
  | indexed (summary : String) (markdown : String)
  deriving BEq, Repr, DecidableEq
-- The row has valid references and two already parsed Summary spans.
def implementation (first second markdown : String) : Outcome :=
  match ''' + selected + ''' with
  | none => .failed
  | some value => .indexed value markdown
-- Independent requirement: retain the first value and original Markdown.
def specification (first second markdown : String) : Outcome :=
  .indexed first markdown
example : implementation "first" "second" "## Summary\\nfirst\\n## Summary\\nsecond\\n" ''' + ('≠' if tag == 'before' else '=') + '''
    specification "first" "second" "## Summary\\nfirst\\n## Summary\\nsecond\\n" := by decide
#eval IO.println "''' + ('mismatch' if tag == 'before' else 'no_mismatch_in_case') + '''"
'''


def analyze(checkout, lean):
    tag, source, markdown = bind(checkout)
    with tempfile.TemporaryDirectory() as tmp:
        proof = Path(tmp) / 'summary.lean'
        proof.write_text(lean_model(tag))
        p = subprocess.run([lean, str(proof)], capture_output=True, text=True, timeout=120)
    expected = 'mismatch\n' if tag == 'before' else 'no_mismatch_in_case\n'
    if p.returncode or p.stdout != expected:
        raise ValueError('Lean failed: ' + (p.stdout + p.stderr)[:2000])
    return {'status': expected.strip(), 'shape': tag, 'source': str(source.relative_to(checkout)),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'markdown_source': str(markdown.relative_to(checkout)),
            'markdown_sha256': hashlib.sha256(markdown.read_bytes()).hexdigest(),
            'case': 'two already parsed Summary records on a valid row',
            'limits': 'bounded projection; parser and Python-to-Lean equivalence are not proved'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    result = {'findings': [], 'unresolved': []}
    try:
        analysis = analyze(args.checkout.resolve(strict=True), args.lean)
        if analysis['status'] == 'mismatch':
            result['findings'].append({
                'path': analysis['source'],
                'detail': 'Duplicate Summary records raise an error instead of indexing the first Summary.'
            })
    except (OSError, SyntaxError, ValueError, subprocess.TimeoutExpired) as exc:
        result['unresolved'].append(str(exc))
    print(json.dumps(result))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
