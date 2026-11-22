import ts from 'typescript';
import { parse } from 'svelte/compiler';
import { readFileSync } from 'node:fs';

function functionSizes({ path, source }) {
  const ast = path.endsWith('.svelte') ? parse(source, { filename: path }) : null;
  const blocks = ast ? [ast.module, ast.instance].filter(Boolean).map(block => block.content) : [{ start: 0, end: source.length }];
  return blocks.flatMap(block => scriptSizes(path, source, block.start, block.end));
}

function scriptSizes(path, source, offset, endOffset) {
  const tree = ts.createSourceFile(path, source.slice(offset, endOffset), ts.ScriptTarget.Latest, true);
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
      const start = source.slice(0, offset + node.getStart(tree)).split(/\r\n|[\n\r\u2028\u2029]/).length - 1;
      const end = source.slice(0, offset + node.end - 1).split(/\r\n|[\n\r\u2028\u2029]/).length - 1;
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
