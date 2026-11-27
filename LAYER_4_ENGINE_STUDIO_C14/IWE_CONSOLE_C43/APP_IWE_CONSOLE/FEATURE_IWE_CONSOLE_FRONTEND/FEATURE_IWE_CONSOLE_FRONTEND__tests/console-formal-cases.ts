import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { expect } from '@playwright/test';

type Field = [event: string, field: string];
export type CorrelatedCase = { name: string; same_values: [Field, Field][] };

export function checkObservedValues(scenario: CorrelatedCase, events: Record<string, Record<string, unknown>>) {
  for (const [[left, from], [right, to]] of scenario.same_values) {
    const source = events[left]?.[from];
    expect(source, `${scenario.name}: ${left}.${from}`).toBeDefined();
    expect(events[right]?.[to], `${scenario.name}: ${right}.${to}`).toEqual(source);
  }
}

export function formalCases<T>(...actions: string[]): Record<string, T[]> {
  const root = resolve(import.meta.dirname, '../../../../..');
  const engine = resolve(root, 'LAYER_4_ENGINE_STUDIO_C14');
  const python = process.env.C46_FORMAL_PYTHON ?? resolve(root,
    'LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv/bin/python');
  const driver = resolve(engine, 'FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/console_case_driver.py');
  return JSON.parse(execFileSync(python, ['-B', driver, ...actions], {
    encoding: 'utf8', env: { ...process.env, PYTHONPATH: engine },
  })) as Record<string, T[]>;
}
