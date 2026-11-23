import { defineConfig } from '@playwright/test';

const baseURL = process.env.WORKBENCH_E2E_URL;

if (!baseURL) throw new Error('WORKBENCH_E2E_URL is required for Workbench browser E2E tests.');

export default defineConfig({
  testDir: './FEATURE_WORKBENCH_FRONTEND__tests',
  testMatch: '**/*.e2e.spec.ts',
  outputDir: '../../../../../.anechoic_tmp/workbench/browser-results',
  timeout: 120_000,
  workers: 1,
  retries: 0,
  use: { baseURL, browserName: 'chromium', channel: 'chromium' },
});
