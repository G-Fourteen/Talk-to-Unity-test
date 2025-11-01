const { test, expect } = require('@playwright/test');

test('should generate text and image', async ({ page }) => {
  await page.goto('http://127.0.0.1:5500/index.html');

  // Generate text
  await page.click('#text-generation-btn');
  await page.waitForSelector('#text-output');
  const textOutput = await page.textContent('#text-output');
  expect(textOutput).not.toBeNull();

  // Generate image
  await page.click('#image-generation-btn');
  await page.waitForSelector('#image-output');
  const imageOutput = await page.getAttribute('#image-output', 'src');
  expect(imageOutput).not.toBeNull();
});
