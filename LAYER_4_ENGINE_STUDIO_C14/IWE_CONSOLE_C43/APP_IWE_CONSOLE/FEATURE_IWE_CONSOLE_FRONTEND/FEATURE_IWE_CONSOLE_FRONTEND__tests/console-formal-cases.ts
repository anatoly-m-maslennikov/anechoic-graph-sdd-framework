import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { isDeepStrictEqual } from 'node:util';
import { expect } from '@playwright/test';

type Field = [event: string, field: string];
export type Effect = [target: string, outcome: string, detail?: Record<string, unknown>];
export type EffectCase = { name: string; must_effect: Effect[]; forbid_effect: string[]; must_precede: [Effect, Effect][] };
export type CorrelatedCase = EffectCase & { same_values: [Field, Field][] };

function matchesDetail(actual: unknown, required: unknown) {
  if (isDeepStrictEqual(actual, required)) return true;
  return typeof actual === 'number' && Number.isSafeInteger(actual) && actual >= 0
    && required !== null && typeof required === 'object' && Object.keys(required).length === 1
    && 'at_most' in required && typeof required.at_most === 'number' && actual <= required.at_most;
}

function matchesEffect([target, outcome, detail = {}]: Effect, required: Effect) {
  return target === required[0] && outcome === required[1]
    && Object.entries(required[2] ?? {}).every(([field, value]) => matchesDetail(detail[field], value));
}

export function checkObservedEffects(scenario: EffectCase, observations: Effect[]) {
  const first = (effect: Effect) => observations.findIndex(observed => matchesEffect(observed, effect));
  for (const required of scenario.must_effect) {
    expect(first(required), `${scenario.name}: missing effect ${JSON.stringify(required)}`).toBeGreaterThanOrEqual(0);
  }
  for (const target of scenario.forbid_effect) {
    expect(observations.some(effect => effect[0] === target), `${scenario.name}: forbidden effect ${target}`).toBe(false);
  }
  for (const [before, after] of scenario.must_precede) {
    const next = first(after);
    if (next < 0) continue;
    const earlier = first(before);
    expect(earlier >= 0 && earlier < next,
      `${scenario.name}: ${JSON.stringify(before)} must precede ${JSON.stringify(after)}`).toBe(true);
  }
}

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
