import { readFileSync } from 'node:fs';
import { act, fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import App from './App';

// Real released artifacts; only transport is mocked. No fabricated metrics.
beforeEach(() => {
  window.history.replaceState(null, '', '/');
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    const name = String(url).match(/data\/([a-z]+)\.v1\.json$/)?.[1];
    if (!name) throw new Error('MOCK unavailable backend/geometry');
    return { ok: true, json: async () => JSON.parse(readFileSync(`public/data/${name}.v1.json`, 'utf8')) };
  }));
});

it('opens with all languages, SDG art and one accessible act; Next/Back focuses the act heading', async () => {
  render(<App />);
  expect(await screen.findByLabelText('Selected language')).toHaveValue('all');
  expect(screen.getByRole('img', { name: 'UN Sustainable Development Goal 10: Reduced Inequalities.' })).toBeVisible();
  expect(screen.queryByText('Language should never be a barrier to being heard.')).not.toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Hear What AI Hears' })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Next: Investigate' }));
  const pilotPicker = within(screen.getByRole('combobox', { name: 'Selected language' }));
  expect(pilotPicker.getByRole('option', { name: 'Choose a language' })).toBeDisabled();
  expect(pilotPicker.getAllByRole('option').filter(option => !(option as HTMLOptionElement).disabled)
    .map(option => option.textContent).sort()).toEqual(['Arabic', 'Cantonese', 'English', 'Mandarin Chinese', 'Punjabi', 'Urdu']);
  expect(screen.getByRole('heading', { name: 'Hear What AI Hears' })).toHaveFocus();
  expect(screen.queryByRole('heading', { name: /Language coverage by ward/ })).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: '02 Investigate' })).toHaveAttribute('aria-current', 'step');
  fireEvent.click(screen.getByRole('button', { name: '← Back' }));
  expect(screen.getByRole('heading', { name: /Language coverage by ward/ })).toHaveFocus();
  expect(screen.getByRole('option', { name: 'Bengali' })).toBeInTheDocument();
});

it('preserves ward, metric, selected recording and recovery session across acts and pauses inactive audio', async () => {
  render(<App />);
  await screen.findByLabelText('Selected language');
  fireEvent.change(screen.getByLabelText('Selected language'), { target: { value: 'urdu' } });
  fireEvent.click(await screen.findByRole('button', { name: 'Ward 10' }));
  fireEvent.click(screen.getByRole('button', { name: 'Share of language base' }));
  fireEvent.click(screen.getByRole('button', { name: 'Next: Investigate' }));
  const player = await screen.findByLabelText('FLEURS recording urdu-1533');
  expect(screen.queryByRole('combobox', { name: /^Recording$/ })).not.toBeInTheDocument();
  const pause = vi.spyOn(player as HTMLAudioElement, 'pause');
  fireEvent.click(screen.getByRole('button', { name: 'Next: Demonstrate' }));
  expect(pause).toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText('Demo route'), { target: { value: 'offline' } });
  fireEvent.change(screen.getByLabelText('Prerecorded sample'), { target: { value: 'urdu-1533' } });
  fireEvent.click(screen.getByRole('button', { name: 'Start saved simulation' }));
  expect(screen.getByText('State: confirm')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Return to Discover' }));
  fireEvent.click(screen.getByRole('button', { name: '03 Demonstrate' }));
  expect(screen.getByText('State: confirm')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: '← Back' }));
  expect(screen.getByLabelText('FLEURS recording urdu-1533')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: '← Back' }));
  const detail = within(screen.getByRole('complementary', { name: 'Selected ward demographics' }));
  expect(detail.getByText('4,520')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Share of language base' })).toHaveAttribute('aria-pressed', 'true');
});

it('supports direct fragment entry and internal continuation without exposing inactive acts', async () => {
  window.history.replaceState(null, '', '/#demonstrate');
  render(<App />);
  fireEvent.change(await screen.findByLabelText('Selected language'), { target: { value: 'urdu' } });
  fireEvent.change(await screen.findByLabelText('Demo route'), { target: { value: 'offline' } });
  fireEvent.change(screen.getByLabelText('Prerecorded sample'), { target: { value: 'urdu-1533' } });
  fireEvent.click(screen.getByRole('button', { name: 'Start saved simulation' }));
  fireEvent.click(screen.getByRole('button', { name: /\(Correct\)/ }));
  expect(screen.getByText('State: accepted')).toBeVisible();
  expect(screen.getByRole('link', { name: 'Return to ward map' })).toHaveAttribute('href', '#discover');
  expect(screen.queryByRole('button', { name: /Recommend/ })).not.toBeInTheDocument();
  await act(async () => {
    window.location.hash = 'recommend';
    window.dispatchEvent(new HashChangeEvent('hashchange'));
  });
  expect(screen.getByRole('heading', { name: 'Language coverage by ward' })).toHaveFocus();
  const coverage = within(screen.getByRole('figure', { name: 'Supplied task-audio coverage gap' }));
  expect(coverage.getByText('52.1%')).toBeVisible();
  expect(coverage.getByText(/79,940 of 153,480 across 14 tracked/)).toBeVisible();
  expect(screen.queryByRole('button', { name: /\(Correct\)/ })).not.toBeInTheDocument();
});

it('rejects invalid research payloads with a usable navigation shell and no invented census values', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) }));
  render(<App />);
  expect(await screen.findByText(/No demographic values are displayed/)).toBeVisible();
  expect(screen.queryByText('79,940')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Next: Investigate' }));
  expect(screen.getByRole('heading', { name: 'Hear What AI Hears' })).toBeVisible();
});
