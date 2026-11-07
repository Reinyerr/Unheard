import { expect, test } from '@playwright/test';

// Live local integration preflight, separate from mocked unit tests.
// Run once with FastAPI started, then with it stopped and EXPECT_BACKEND=offline.
for (const viewport of [{ width: 1280, height: 900 }, { width: 375, height: 812 }]) {
  test(`local shell and health at ${viewport.width}px`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setViewportSize(viewport);
    await page.goto('/');
    const offline = process.env.EXPECT_BACKEND === 'offline';
    await expect(page.getByRole('status')).toContainText(offline ? 'Backend unavailable' : 'Backend connected');
    if (offline) {
      await expect(page.getByText(/Start FastAPI/)).toBeVisible();
      await page.getByRole('button', { name: 'Retry connection' }).click();
      await expect(page.getByRole('status')).toContainText('Backend unavailable');
    }
    await expect(page.getByText('Research data not loaded')).toBeVisible();
    await expect(page.getByText('Planned', { exact: true })).toHaveCount(4);
    await page.getByRole('link', { name: '04 Recommend' }).click();
    await expect(page).toHaveURL(/#recommend$/);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    await page.screenshot({ path: `test-results/bootstrap-${viewport.width}-${offline ? 'offline' : 'online'}.png`, fullPage: true });
  });
}
