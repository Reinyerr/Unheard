import { readFileSync } from 'node:fs';
import { webcrypto } from 'node:crypto';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import { validateArtifact } from './types/research';
import { SelectionProvider, initialSelection, selectionReducer } from './state/selection';
import LanguageSelector from './components/LanguageSelector';
import WardExplorer from './features/map/WardExplorer';
import SpeechLab from './features/speech-lab/SpeechLab';
import Recovery from './features/recovery/Recovery';
import { loadWardGeometry } from './data/wardGeometry';
import { delta, percent } from './features/speech-lab/data';

// Read-only released artifacts; mocks replace transport, never research values.
const read = (name: string) => JSON.parse(readFileSync(`public/data/${name}.v1.json`, 'utf8'));
const languages = validateArtifact('languages', read('languages'));
const wards = validateArtifact('wards', read('wards'));
const samples = validateArtifact('samples', read('samples'));
const experiments = validateArtifact('experiments', read('experiments'));
const census = { status: 'ready', data: { languages, wards } };
vi.mock('./data/ResearchData', () => ({ useResearch: () => ({ census, experiments: { status: 'ready', data: experiments }, reload: vi.fn() }) }));
vi.mock('./features/speech-lab/data', async importOriginal => ({ ...await importOriginal<typeof import('./features/speech-lab/data')>(),
  useSamples: () => ({ resource: { status: 'ready', data: samples }, reload: vi.fn() }) }));

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('MOCK offline')));
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
});

it('selects a ward in the labelled geometry fallback and retains count/share/base on toggle', async () => {
  render(<SelectionProvider><LanguageSelector /><WardExplorer /></SelectionProvider>);
  expect(await screen.findByText(/Verified ward table — map unavailable/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Selected language'), { target: { value: 'urdu' } });
  fireEvent.click(screen.getByRole('button', { name: 'Ward 10' }));
  const detail = within(screen.getByRole('complementary', { name: 'Selected ward demographics' }));
  for (const text of ['4,520', '6.12%', '73,830']) expect(detail.getByText(text)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Share of language base' }));
  expect(screen.getByRole('button', { name: 'Share of language base' })).toHaveAttribute('aria-pressed', 'true');
  expect(detail.getByText('4,520')).toBeInTheDocument();
});

it('automatically shows the featured recording and keeps incompatible comparisons unavailable', () => {
  render(<SelectionProvider><LanguageSelector /><SpeechLab /></SelectionProvider>);
  const language = screen.getByLabelText('Selected language');
  fireEvent.change(language, { target: { value: 'tamil' } });
  expect(screen.getByText('Select a language above to hear its featured recording.')).toBeVisible();
  expect(screen.queryByText('0.0%')).not.toBeInTheDocument();
  fireEvent.change(language, { target: { value: 'urdu' } });
  expect(screen.getAllByRole('combobox')).toHaveLength(1);
  expect(screen.getByLabelText('FLEURS recording urdu-1533')).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Reference text' })).toBeVisible();
  expect(screen.queryByRole('link', { name: /Read reference transcript|Compare saved transcriptions/i })).not.toBeInTheDocument();
  const comparison = within(screen.getByRole('region', { name: 'Comparison' }));
  expect(comparison.getByRole('heading', { name: 'Did the hint help?' })).toBeVisible();
  expect(comparison.queryByText(/Character error rate is the number/)).not.toBeInTheDocument();
  expect(screen.getByRole('region', { name: 'Without a language hint transcription' })).toBeInTheDocument();
  expect(screen.getByText('No change in error rate')).toBeVisible();
  fireEvent.change(language, { target: { value: 'arabic' } });
  expect(screen.queryByLabelText('FLEURS recording urdu-1533')).not.toBeInTheDocument();
  expect(screen.getByLabelText('FLEURS recording arabic-1533')).toBeInTheDocument();
  expect(HTMLMediaElement.prototype.pause).toHaveBeenCalled();
  fireEvent.change(language, { target: { value: 'english' } });
  expect(screen.getByText('31.1 percentage points lower with the hint on this recording.')).toBeVisible();
  fireEvent.change(language, { target: { value: 'cantonese' } });
  expect(screen.getByText('Comparison unavailable')).toBeVisible();
});

it('rejects stale results while ward selection preserves speech state; formats uncapped metrics', () => {
  const sample = samples.samples.find(s => s.sample_id === 'urdu-1533')!;
  const result = experiments.records.find(r => r.sample_id === sample.sample_id)!;
  let state = selectionReducer(initialSelection, { type: 'language', value: 'urdu' });
  const revision = state.language_revision;
  state = selectionReducer(state, { type: 'sample', value: sample, revision });
  state = selectionReducer(state, { type: 'result', value: result, revision });
  state = selectionReducer(state, { type: 'ward', value: 10 });
  expect(state.selected_result).toEqual(result);
  state = selectionReducer(state, { type: 'language', value: 'arabic' });
  expect(selectionReducer(state, { type: 'result', value: result, revision }).selected_result).toBeNull();
  expect(percent(1.2)).toBe('120.0%');
  expect(percent(null)).toBe('Not available');
  expect(delta(.1)).toBe('+10.0 percentage points');
});

it('runs saved Urdu confirmation without backend and preserves explicit referral on unavailable retry', async () => {
  render(<SelectionProvider><LanguageSelector /><Recovery /></SelectionProvider>);
  fireEvent.change(screen.getByLabelText('Selected language'), { target: { value: 'urdu' } });
  fireEvent.change(screen.getByLabelText('Demo route'), { target: { value: 'offline' } });
  fireEvent.change(screen.getByLabelText('Prerecorded sample'), { target: { value: 'urdu-1533' } });
  fireEvent.click(screen.getByRole('button', { name: 'Start saved simulation' }));
  expect(screen.getByText('State: confirm')).toBeInTheDocument();
  expect(screen.getByText(/Text-only confirmation/)).toBeInTheDocument();
  expect(screen.getByText(/Judge-controlled interaction simulation/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: /\(Incorrect\)/ }));
  fireEvent.change(screen.getByLabelText('Different recording for the single simulated retry'), { target: { value: 'urdu-1537' } });
  fireEvent.click(screen.getByRole('button', { name: 'Try Different Sample' }));
  expect(screen.getByText('State: referral')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Try Different Sample' })).not.toBeInTheDocument();
});

it('loads exactly matching geometry and fails closed when a polygon is missing', async () => {
  vi.stubGlobal('crypto', webcrypto);
  const geometry = JSON.parse(readFileSync('public/data/mississauga_wards.geojson', 'utf8'));
  for (const remove of [false, true]) {
    const value = structuredClone(geometry);
    if (remove) value.features.pop();
    const bytes = new TextEncoder().encode(JSON.stringify(value));
    const hash = Buffer.from(await webcrypto.subtle.digest('SHA-256', bytes)).toString('hex');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ schema_version: '1.0', status: 'validated', map_ready: true,
      geometry_file: 'mississauga_wards.geojson', geometry_sha256: hash, ward_ids: wards.wards.map(w => w.ward_id) }) })
      .mockResolvedValueOnce({ ok: true, arrayBuffer: async () => bytes.buffer }));
    expect((await loadWardGeometry(wards)).status).toBe(remove ? 'unavailable' : 'ready');
  }
});
