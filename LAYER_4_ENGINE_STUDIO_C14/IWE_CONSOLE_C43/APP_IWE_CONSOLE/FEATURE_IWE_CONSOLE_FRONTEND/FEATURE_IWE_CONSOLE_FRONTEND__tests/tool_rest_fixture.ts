import type { Route } from '@playwright/test';

export function toolRequest(route: Route): {
  name: string;
  arguments: Record<string, unknown>;
} {
  return route.request().postDataJSON();
}

export function toolReply(route: Route, value: unknown) {
  const instance_id = route.request().headers()['x-anechoic-project-instance'];
  if (!instance_id || !/^[0-9a-f]{64}$/.test(instance_id)) {
    throw new Error('Browser Tool request lacks an admitted Project instance.');
  }
  return {
    result: { value, text: null },
    project: { prefix: 'AN', instance_id },
  };
}
