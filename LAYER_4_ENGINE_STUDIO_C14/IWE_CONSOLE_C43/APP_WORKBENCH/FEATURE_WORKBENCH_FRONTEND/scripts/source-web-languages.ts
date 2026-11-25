import { readFileSync } from 'node:fs';
import { parse } from 'svelte/compiler';

type Input = { path: string; source: string };

function findings({ path, source }: Input): string[] {
  try {
    const tree = parse(source, { filename: path, modern: true });
    const messages: string[] = [];
    for (const script of [tree.module, tree.instance]) {
      if (!script?.content.body.length) continue;
      const language = script.attributes.find((attribute) => attribute.name === 'lang')?.value;
      if (Array.isArray(language) && language.length === 1 &&
          language[0].type === 'Text' && language[0].data === 'ts') continue;
      const line = source.slice(0, script.start).split(/\r\n?|\n/).length;
      messages.push(`${path}:${line}: Svelte script must use lang="ts"`);
    }
    return messages;
  } catch (error) {
    return [`${path}: cannot parse Svelte source: ${String(error)}`];
  }
}

const sources: Input[] = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(sources.flatMap(findings)));
