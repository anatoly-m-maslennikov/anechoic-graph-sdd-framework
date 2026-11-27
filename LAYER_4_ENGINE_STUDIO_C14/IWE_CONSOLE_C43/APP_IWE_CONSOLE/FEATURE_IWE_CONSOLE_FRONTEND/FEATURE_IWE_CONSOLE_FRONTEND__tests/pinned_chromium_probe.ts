import { chromium } from "@playwright/test";

const timeout: number | undefined =
  process.env.ANECHOIC_TEST_IMAGE_DEADLINES === "0" ? 0 : undefined;
const browser = await chromium.launch({ channel: "chromium", timeout });
console.log(browser.version());
await browser.close();
