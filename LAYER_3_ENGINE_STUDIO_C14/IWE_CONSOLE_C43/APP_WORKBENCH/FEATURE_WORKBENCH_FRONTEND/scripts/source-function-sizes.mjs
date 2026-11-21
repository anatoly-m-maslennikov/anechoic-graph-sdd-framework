import ts from 'typescript';
import { readFileSync } from 'node:fs';

function functionSizes({ path, source }) {
  const tree = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);
  if (tree.parseDiagnostics.length) {
    const { messageText } = tree.parseDiagnostics[0];
    const diagnostic = ts.flattenDiagnosticMessageText(messageText, ' ');
    throw new Error(`${path}: ${diagnostic}`);
  }
  const lines = source.split(/\r\n|[\n\r\u2028\u2029]/);
  const result = [];
  function visit(node) {
    if (ts.isFunctionLike(node) && node.body) {
      const name = ts.isConstructorDeclaration(node) ? 'constructor' :
        node.name?.getText(tree) || node.parent?.name?.getText(tree) ||
        '<anonymous>';
      const offset = node.getStart(tree);
      const start = tree.getLineAndCharacterOfPosition(offset).line;
      const end = tree.getLineAndCharacterOfPosition(node.end - 1).line;
      const range = lines.slice(start, end + 1);
      const size = range.filter(line => line.trim()).length;
      result.push([start + 1, name, size]);
    }
    ts.forEachChild(node, visit);
  }
  visit(tree);
  return result;
}

const input = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(input.map(functionSizes)));
