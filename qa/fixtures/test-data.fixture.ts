import { test as base } from '@playwright/test';

type TestDataFixtures = {
  productKey: string;
};

export const test = base.extend<TestDataFixtures>({
  productKey: async ({}, use) => {
    await use(process.env.AUTOQA_PRODUCT_KEY ?? 'erp');
  },
});

export { expect } from '@playwright/test';

