import { webcrypto } from 'node:crypto';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import PromptAudio from './PromptAudio';
import { PROMPT_REVISION, recoveryPrompt, TTS_ATTRIBUTION, TTS_MODEL } from './prompts';

// MOCK bytes only. This tests approval gating, not human language/audio quality.
it('plays only a matching approved hash, falls back on playback error, and disposes audio', async () => {
  vi.stubGlobal('crypto', webcrypto);
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
  const create = vi.fn(() => 'blob:mock');
  const revoke = vi.fn();
  vi.stubGlobal('URL', class extends URL { static createObjectURL = create; static revokeObjectURL = revoke; });
  const bytes = new Uint8Array(201);
  const config = recoveryPrompt('urdu')!;
  const manifest = { ...config, schema_version: '2.0', language_id: 'urdu', prompt_revision: PROMPT_REVISION,
    provider: 'elevenlabs', model_id: TTS_MODEL, generated_at_utc: '2026-11-07T00:00:00Z', origin: 'saved',
    audio_path: 'audio/prompts/urdu/confirm.mp3', audio_sha256: Buffer.from(await webcrypto.subtle.digest('SHA-256', bytes)).toString('hex'),
    review_status: 'approved', human_listened: true, language_reviewed: true, approved_at_utc: '2026-11-07T00:00:00Z',
    rights_reviewed: true, attribution: TTS_ATTRIBUTION,
    verification: { synthesis_http_status: 200, model_language_advertised: true, voice_access: 'accessible' } };
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => manifest })
    .mockResolvedValueOnce({ ok: true, arrayBuffer: async () => bytes.buffer });
  vi.stubGlobal('fetch', fetchMock);
  const { unmount } = render(<PromptAudio language="urdu" />);
  const player = await screen.findByLabelText('Cached simulated confirmation instruction');
  expect(player).toHaveAttribute('src', 'blob:mock');
  fireEvent.error(player);
  expect(screen.getByText(/Text-only confirmation/)).toBeInTheDocument();
  unmount();
  expect(revoke).toHaveBeenCalledWith('blob:mock');
});

it('never fetches audio for unapproved metadata', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ review_status: 'pending_review' }) });
  vi.stubGlobal('fetch', fetchMock);
  render(<PromptAudio language="urdu" />);
  await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());
  expect(screen.getByText(/Text-only confirmation/)).toBeInTheDocument();
  expect(screen.queryByLabelText('Cached simulated confirmation instruction')).not.toBeInTheDocument();
});
