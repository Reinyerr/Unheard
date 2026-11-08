import { expect, test, type Page } from '@playwright/test';

// Real localhost app, published research and restored FLEURS audio. Fault routes
// only abort requests; they never supply fabricated research/provider responses.
test.beforeEach(async ({ page }) => {
  await page.route('**/*', route => {
    const host = new URL(route.request().url()).hostname;
    return ['127.0.0.1', 'localhost'].includes(host) ? route.continue() : route.abort();
  });
});

async function urdu(page: Page) {
  await page.goto('/');
  await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption('urdu');
}

test('network-unreachable backend retains the complete saved journey without provider replay', async ({ page }) => {
  let backendPosts = 0;
  page.on('request', request => { if (request.url().includes(':8000/') && request.method() === 'POST') backendPosts++; });
  await page.route('http://127.0.0.1:8000/**', route => route.abort('connectionrefused'));
  await urdu(page);
  await page.getByRole('button', { name: 'Next: Investigate' }).click();
  await page.getByRole('combobox', { name: 'Recording', exact: true }).selectOption('urdu-1533');
  await expect(page.getByRole('region', { name: 'Automatic detection transcription' }).getByText('10.6%', { exact: true })).toBeVisible();
  const audio = page.getByLabel('FLEURS recording urdu-1533', { exact: true });
  await audio.evaluate(async (node: HTMLAudioElement) => node.play());
  await expect.poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime)).toBeGreaterThan(0);
  await page.getByRole('button', { name: 'Next: Demonstrate' }).click();
  await expect(page.getByText(/Backend unavailable · saved browser route/)).toBeVisible();
  await page.getByLabel('Demo route').selectOption('offline');
  await page.getByLabel('Prerecorded sample').selectOption('urdu-1533');
  await page.getByRole('button', { name: 'Start saved simulation' }).click();
  await expect(page.getByText('State: confirm', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: /\(Correct\)/ }).click();
  await page.getByRole('link', { name: 'Continue to recommendations' }).click();
  await expect(page.getByRole('heading', { name: 'Urdu: evaluation priority 1' })).toBeVisible();
  await page.getByRole('button', { name: '← Back' }).click();
  await expect(page.getByText('State: accepted', { exact: true })).toBeVisible();
  expect(backendPosts).toBe(0);
});

test('Urdu four acts: real map/audio/metrics, explicit acceptance, one retry/referral and priorities', async ({ page }, info) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await urdu(page);
  const discover = page.locator('#discover');
  const lab = page.locator('#investigate');
  const recovery = page.locator('#demonstrate');
  const recommend = page.locator('#recommend');
  await expect(discover.getByRole('button', { name: /^Ward 10;/ })).toBeVisible();
  await discover.getByRole('button', { name: /^Ward 10;/ }).press('Enter');
  const detail = discover.getByRole('complementary', { name: 'Selected ward demographics' });
  for (const value of ['4,520', '6.12%', '73,830']) await expect(detail.getByText(value, { exact: true })).toBeVisible();
  await discover.getByRole('button', { name: 'Share of language base', exact: true }).click();
  await expect(discover.getByRole('button', { name: 'Share of language base', exact: true })).toHaveAttribute('aria-pressed', 'true');

  await page.getByRole('button', { name: '02 Investigate' }).click();
  await lab.getByRole('combobox', { name: 'Recording', exact: true }).selectOption('urdu-1533');
  const audio = lab.getByLabel('FLEURS recording urdu-1533', { exact: true });
  await audio.evaluate(async (node: HTMLAudioElement) => { await node.play(); });
  await expect.poll(() => audio.evaluate((node: HTMLAudioElement) => node.currentTime)).toBeGreaterThan(.1);
  await expect.poll(() => audio.evaluate((node: HTMLAudioElement) => node.duration)).toBeGreaterThan(0);
  await audio.evaluate((node: HTMLAudioElement) => node.pause());
  for (const mode of ['Automatic detection transcription', 'Guided language transcription']) {
    const panel = lab.getByRole('region', { name: mode });
    await expect(panel.getByText('10.6%', { exact: true })).toBeVisible();
    await expect(panel.getByText('WER', { exact: true })).toHaveCount(0);
    await expect(panel.locator('[dir="rtl"]').first()).toBeVisible();
  }
  await expect(lab.getByText('0.0 percentage points', { exact: true }).first()).toBeVisible();
  await lab.getByText('Language pilot summary · sample counts and limitations', { exact: true }).click();
  await expect(lab.getByText(/Selected n=8; scored automatic n=1; scored guided n=1; comparable pairs n=1/)).toBeVisible();

  await page.getByRole('button', { name: '03 Demonstrate' }).click();
  await recovery.getByLabel('Demo route').selectOption('offline');
  await recovery.getByLabel('Prerecorded sample').selectOption('urdu-1533');
  await recovery.getByRole('button', { name: 'Start saved simulation' }).click();
  await expect(recovery.getByText('State: confirm', { exact: true })).toBeVisible();
  await expect(recovery.getByText(/Text-only confirmation/)).toBeVisible();
  await expect(recovery.getByText(/Judge-controlled interaction simulation/)).toBeVisible();
  await recovery.getByRole('button', { name: /\(Correct\)/ }).click();
  await expect(recovery.getByText('State: accepted', { exact: true })).toBeVisible();
  await recovery.getByRole('button', { name: 'Start separate saved browser simulation' }).click();
  await recovery.getByLabel('Prerecorded sample').selectOption('urdu-1533');
  await recovery.getByRole('button', { name: 'Start saved simulation' }).click();
  await recovery.getByRole('button', { name: /\(Incorrect\)/ }).click();
  await recovery.getByLabel('Different recording for the single simulated retry').selectOption('urdu-1537');
  await recovery.getByRole('button', { name: 'Try Different Sample' }).click();
  await expect(recovery.getByText('State: referral', { exact: true })).toBeVisible();
  await expect(recovery.getByRole('button', { name: 'Try Different Sample' })).toHaveCount(0);
  await expect(recovery.getByText(/has not contacted or connected you/)).toBeVisible();

  await page.getByRole('button', { name: '04 Recommend' }).click();
  await expect(recommend.getByRole('heading', { name: 'Urdu: evaluation priority 1' })).toBeVisible();
  const stats = recommend.getByLabel('Supplied task-audio coverage gap');
  for (const value of ['79,940', '52.1%']) await expect(stats.getByText(value, { exact: true })).toBeVisible();
  await expect(stats.getByText(/153,480.*14 tracked/)).toBeVisible();
  await recommend.getByText('Explore recruitment wards · count and share', { exact: true }).click();
  await expect(recommend.getByRole('region', { name: 'Top wards by count', exact: true }).getByRole('link', { name: 'Ward 10' })).toBeVisible();
  await expect(recommend.getByRole('region', { name: 'Top wards by share', exact: true })).toBeVisible();
  expect(errors).toEqual([]);
  await page.screenshot({ path: info.outputPath('four-acts.png'), fullPage: true });
});

test('language switches clear playback/results; incomplete and incompatible metrics stay unavailable', async ({ page }) => {
  await urdu(page);
  await page.getByRole('button', { name: '02 Investigate' }).click();
  const lab = page.locator('#investigate');
  await lab.getByRole('combobox', { name: 'Recording', exact: true }).selectOption('urdu-1533');
  const oldAudio = await lab.getByLabel('FLEURS recording urdu-1533', { exact: true }).elementHandle();
  await oldAudio!.evaluate(async (node: HTMLAudioElement) => { await node.play(); });
  await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption('arabic');
  await expect(lab.getByLabel('FLEURS recording urdu-1533', { exact: true })).toHaveCount(0);
  expect(await oldAudio!.evaluate((node: HTMLAudioElement) => node.paused)).toBe(true);
  await lab.getByRole('combobox', { name: 'Recording', exact: true }).selectOption('arabic-1537');
  await expect(lab.getByRole('region', { name: 'Automatic detection transcription' }).getByText('Not tested', { exact: true }).first()).toBeVisible();
  await expect(lab.getByText('0.0%', { exact: true })).toHaveCount(0);
  for (const language of ['english', 'punjabi', 'mandarin_chinese']) {
    await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption(language);
    await lab.getByRole('combobox', { name: 'Recording', exact: true }).selectOption(`${language}-1537`);
    await expect(lab.getByRole('region', { name: 'Automatic detection transcription' }).getByText('Not tested', { exact: true }).first()).toBeVisible();
  }
  await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption('cantonese');
  await lab.getByRole('combobox', { name: 'Recording', exact: true }).selectOption('cantonese-1533');
  await expect(lab.getByRole('region', { name: 'Automatic detection transcription' }).getByText(/excluded from comparable metrics/)).toBeVisible();
  await expect(lab.getByRole('region', { name: 'Guided language transcription' }).getByText('10.0%', { exact: true })).toBeVisible();
  await page.getByRole('combobox', { name: 'Selected language', exact: true }).selectOption('tamil');
  await expect(lab.getByText('Not tested', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: '03 Demonstrate' }).click();
  await expect(page.locator('#demonstrate').getByText('Not tested', { exact: true })).toBeVisible();
});

test('missing polygons and invalid audio retain verified table and saved text', async ({ page }) => {
  await page.route('**/data/mississauga_wards.geojson', route => route.abort());
  await page.route('**/audio/**/*.flac', route => route.abort());
  await urdu(page);
  await expect(page.locator('#discover').getByText(/Verified ward table — map unavailable/)).toBeVisible();
  await page.getByRole('button', { name: '02 Investigate' }).click();
  await page.locator('#investigate').getByRole('combobox', { name: 'Recording', exact: true }).selectOption('urdu-1533');
  await page.getByLabel('FLEURS recording urdu-1533', { exact: true }).evaluate((node: HTMLAudioElement) => { void node.play().catch(() => {}); });
  await expect(page.getByText(/Audio unavailable or unsupported/)).toBeVisible();
  await expect(page.locator('#investigate').getByRole('region', { name: 'Automatic detection transcription' }).getByText('10.6%', { exact: true })).toBeVisible();
});

for (const asset of ['wards', 'samples', 'experiments', 'recommendations']) {
  test(`missing ${asset} data fails explicitly without replacing evidence`, async ({ page }) => {
    await page.route(`**/data/${asset}.v1.json`, route => route.abort());
    if (asset === 'wards') {
      await page.goto('/');
      await expect(page.locator('#discover').getByText(/No demographic values are displayed/)).toBeVisible();
      await expect(page.locator('#discover').getByRole('button', { name: 'Ward 10', exact: true })).toHaveCount(0);
      return;
    }
    await urdu(page);
    if (asset === 'samples' || asset === 'experiments') await page.getByRole('button', { name: '02 Investigate' }).click();
    if (asset === 'samples') await expect(page.locator('#investigate').getByText(/vetted sample manifest is unavailable/)).toBeVisible();
    if (asset === 'experiments') {
      await expect(page.locator('#investigate').getByText(/Saved experiment evidence is unavailable/)).toBeVisible();
      await page.getByRole('button', { name: '03 Demonstrate' }).click();
      await page.locator('#demonstrate').getByLabel('Demo route').selectOption('offline');
      await expect(page.locator('#demonstrate').getByText(/Matching saved experiment evidence is unavailable/)).toBeVisible();
    }
    if (asset === 'recommendations') {
      await page.getByRole('button', { name: '04 Recommend' }).click();
      await expect(page.locator('#recommend').getByText(/Verified recommendation data is unavailable/)).toBeVisible();
    }
    await page.getByRole('button', { name: '01 Discover' }).click();
    await expect(page.locator('#discover').getByRole('button', { name: /^Ward 10;/ })).toBeVisible();
  });
}

test('real backend missing evidence or disconnected backend offers an explicit browser recovery route', async ({ page, request }) => {
  await urdu(page);
  await page.getByRole('button', { name: '03 Demonstrate' }).click();
  const recovery = page.locator('#demonstrate');
  if (process.env.EXPECT_BACKEND === 'offline') {
    await expect(recovery.getByText(/Backend unavailable · saved browser route/)).toBeVisible();
    await expect(recovery.getByRole('button', { name: 'Start saved simulation' })).toBeDisabled();
  } else {
    const response = await request.get('http://127.0.0.1:8000/api/recovery/capabilities');
    expect(response.status()).toBe(200);
    const capabilities = await response.json();
    expect(capabilities.selected_sample_count).toBe(48);
    expect(typeof capabilities.live_configured).toBe('boolean'); // Presence is not connectivity proof; no live request is made.
    expect(capabilities.tts_status).toBe('unavailable');
    const savedIds: string[] = capabilities.languages.find((row: { language_id: string }) => row.language_id === 'urdu').saved_sample_ids_by_mode.auto;
    await recovery.getByLabel('Prerecorded sample').selectOption('urdu-1533');
    await recovery.getByRole('button', { name: 'Start saved simulation' }).click();
    // Local raw evidence is intentionally absent from Git. Both a restored
    // developer workspace and a clone without it must remain operable.
    if (savedIds.includes('urdu-1533')) {
      await expect(recovery.getByText('State: confirm', { exact: true })).toBeVisible();
      await recovery.getByRole('button', { name: /\(Incorrect\)/ }).click();
    } else {
      await expect(recovery.getByRole('alert')).toContainText('No verified saved result');
    }
    await expect(recovery.getByText('State: retry or refer', { exact: true })).toBeVisible();
    // Choose a known recording without saved evidence; never invent a second result.
    expect(savedIds).not.toContain('urdu-1537');
    await recovery.getByLabel('Different recording for the single simulated retry').selectOption('urdu-1537');
    await recovery.getByRole('button', { name: 'Try Different Sample' }).click();
    await expect(recovery.getByText('State: referral', { exact: true })).toBeVisible();
    await recovery.getByRole('button', { name: 'Start separate saved browser simulation' }).click();
  }
  await recovery.getByLabel('Demo route').selectOption('offline');
  await recovery.getByLabel('Prerecorded sample').selectOption('urdu-1533');
  await recovery.getByRole('button', { name: 'Start saved simulation' }).click();
  await expect(recovery.getByText('State: confirm', { exact: true })).toBeVisible();
});
