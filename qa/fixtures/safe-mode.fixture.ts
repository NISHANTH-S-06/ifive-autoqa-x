import { test as base } from '@playwright/test';

const blockedActions = new Set([
  'payment_execution',
  'payroll_execution',
  'record_deletion',
  'approval_execution',
  'iiot_machine_control',
]);

type SafeModeFixtures = {
  assertActionAllowed: (action: string) => Promise<void>;
};

export const test = base.extend<SafeModeFixtures>({
  assertActionAllowed: async ({}, use) => {
    await use(async (action: string) => {
      if ((process.env.AUTOQA_SAFE_MODE ?? 'true') === 'true' && blockedActions.has(action)) {
        throw new Error(`Blocked by AutoQA safe mode: ${action}`);
      }
    });
  },
});

export { expect } from '@playwright/test';

