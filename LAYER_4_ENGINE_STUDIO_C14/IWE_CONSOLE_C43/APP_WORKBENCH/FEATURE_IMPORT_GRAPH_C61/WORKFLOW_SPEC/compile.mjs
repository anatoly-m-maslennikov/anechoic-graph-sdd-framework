import { compile } from './WORKFLOW_SPEC__shared.mjs';

const fail = message => { throw new Error(message); };

try {
  let input = '';
  for await (const chunk of process.stdin) { input += chunk; if (input.length > 1_000_000) fail('input exceeds 1 MB'); }
  const result = compile(JSON.parse(input));
  process.stdout.write(JSON.stringify(result) + '\n');
} catch (error) {
  process.stderr.write(`workflow compilation failed: ${error.message}\n`);
  process.exitCode = 1;
}
