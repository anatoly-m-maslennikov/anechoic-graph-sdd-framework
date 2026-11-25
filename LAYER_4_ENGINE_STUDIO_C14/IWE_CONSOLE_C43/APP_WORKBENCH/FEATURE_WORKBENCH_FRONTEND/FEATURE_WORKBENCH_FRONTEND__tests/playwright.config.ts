import { defineConfig } from '@playwright/test';
import { browserTimeout, browserDeadlinesEnabled } from './browser-deadlines';

const baseURL = process.env.WORKBENCH_E2E_URL;

if (!baseURL) throw new Error('WORKBENCH_E2E_URL is required for Workbench browser E2E tests.');

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.e2e.spec.ts',
  outputDir: '../../../../../../.anechoic_tmp/workbench/browser-results',
  timeout: browserTimeout(120_000),
  expect: { timeout: browserTimeout(5_000) },
  workers: 1,
  retries: 0,
  use: {
    baseURL,
    browserName: 'chromium',
    channel: 'chromium',
    actionTimeout: 0,
    navigationTimeout: 0,
    launchOptions: { timeout: browserDeadlinesEnabled ? undefined : 0 },
  },
});
