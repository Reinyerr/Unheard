import { expect, test } from '@playwright/test';

// Real local artifacts and Leaflet, separate from mocked unit tests.
for (const viewport of [{ width: 1366, height: 768 }, { width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  test(`guided shell, ward lift and persistent state at ${viewport.width}px`, async ({ page }, info) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setViewportSize(viewport);
    await page.goto('/');
    await expect(page.getByLabel('Selected language')).toHaveValue('all');
    await expect(page.locator('.journey-act:visible')).toHaveCount(1);
    await expect(page.getByAltText('UN Sustainable Development Goal 10: Reduced Inequalities.').first()).toBeVisible();
    await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption('urdu');
    const ward = page.getByRole('button', { name: /^Ward 10;/ });
    await ward.press('Enter');
    await expect(ward).toHaveAttribute('aria-pressed', 'true');
    await expect(ward).toHaveClass(/ward-raised/);
    await expect.poll(() => ward.evaluate(node => getComputedStyle(node).translate)).toBe('0px -14px');
    await expect(page.getByRole('button', { name: /^Ward 1;/ })).toHaveAttribute('fill-opacity', '0.24');
    // Decorative bases must not create duplicate keyboard or pointer targets.
    await expect(page.locator('.leaflet-wardBases-pane [tabindex]')).toHaveCount(0);
    await expect(page.locator('.leaflet-wardBases-pane path[aria-hidden="true"]')).toHaveCount(11);
    const detail = page.getByRole('complementary', { name: 'Selected ward demographics' });
    for (const value of ['4,520', '6.12%', '73,830']) await expect(detail.getByText(value, { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Next: Investigate' }).click();
    await expect(page.getByRole('heading', { name: 'Hear What AI Hears' })).toBeFocused();
    const player = page.getByLabel('FLEURS recording urdu-1533', { exact: true });
    await player.evaluate(async (node: HTMLAudioElement) => node.play());
    await page.getByRole('button', { name: 'Next: Demonstrate' }).click();
    expect(await player.evaluate((node: HTMLAudioElement) => node.paused)).toBe(true);
    await page.getByLabel('Demo route').selectOption('offline');
    await page.getByLabel('Prerecorded sample').selectOption('urdu-1533');
    await page.getByRole('button', { name: 'Start saved simulation' }).click();
    await expect(page.getByText('State: confirm', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Return to Discover' }).click();
    await expect(ward).toHaveClass(/ward-raised/);
    await page.getByRole('button', { name: '03 Demonstrate' }).click();
    await expect(page.getByText('State: confirm', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: '← Back' }).click();
    await expect(player).toBeAttached();
    await page.getByRole('button', { name: '← Back' }).click();
    await expect(ward).toHaveClass(/ward-raised/);
    await page.screenshot({ path: info.outputPath(`raised-ward-${viewport.width}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Clear ward selection', exact: true }).click();
    await expect(ward).toHaveAttribute('aria-pressed', 'false');
    await expect(page.getByRole('button', { name: /^Ward 1;/ })).toHaveAttribute('fill-opacity', '0.94');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
  });
}

test('reduced motion, real SVG alignment on zoom/resize, and keyboard-only navigation', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  const ward = page.getByRole('button', { name: /^Ward 10;/ });
  await ward.press('Enter');
  expect(await ward.evaluate(node => getComputedStyle(node).transitionDuration)).toBe('0s');
  for (const width of [1440, 900]) {
    await page.setViewportSize({ width, height: 900 });
    await page.getByRole('button', { name: 'Zoom in', exact: true }).click();
    const surface = await ward.getAttribute('d');
    // The selected surface and its original footprint are reprojected together.
    const footprint = await page.locator('.leaflet-wardBases-pane path').nth(9).getAttribute('d');
    expect(surface).toBe(footprint);
  }
  await page.getByRole('button', { name: 'Next: Investigate' }).press('Enter');
  await expect(page.getByRole('heading', { name: 'Hear What AI Hears' })).toBeFocused();
  await page.getByRole('button', { name: '← Back' }).press('Enter');
  await expect(page.getByRole('heading', { name: /Language coverage by ward/ })).toBeFocused();
  await ward.press('Escape');
  await expect(ward).toHaveAttribute('aria-pressed', 'false');
});

test('browser Back and Forward keep the visible act synchronized with the entry URL', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Next: Investigate' }).click();
  await page.goBack();
  await expect(page.getByRole('heading', { name: /Language coverage by ward/ })).toBeVisible();
  await expect(page.getByRole('button', { name: '01 Discover' })).toHaveAttribute('aria-current', 'step');
  await page.goForward();
  await expect(page.getByRole('heading', { name: 'Hear What AI Hears' })).toBeFocused();
});
