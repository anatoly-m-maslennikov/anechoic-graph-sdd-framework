import ts from 'typescript';
import { readFileSync } from 'node:fs';

function functionSizes({ path, source }) {
  const tree = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);
  if (tree.parseDiagnostics.length) {
    throw new Error(`${path}: ${ts.flattenDiagnosticMessageText(tree.parseDiagnostics[0].messageText, ' ')}`);
  }
  const result = [];
  function visit(node) {
    if (ts.isFunctionLike(node) && node.body) {
      const name = ts.isConstructorDeclaration(node) ? 'constructor' :
        node.name?.getText(tree) || node.parent?.name?.getText(tree) || '<anonymous>';
      const start = tree.getLineAndCharacterOfPosition(node.getStart(tree)).line;
      const end = tree.getLineAndCharacterOfPosition(node.end - 1).line;
      result.push([start + 1, name, end - start + 1]);
    }
    ts.forEachChild(node, visit);
  }
  visit(tree);
  return result;
}

const input = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(input.map(functionSizes)));
