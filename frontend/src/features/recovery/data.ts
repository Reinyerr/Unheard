import { z } from 'zod';
import { experimentStatus, languageId, type Experiments, type Samples } from '../../types/research';
import { recoveryPrompt } from './prompts';

export const API = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export const NOTICE = 'Prerecorded third-party speech. Confirmation is a simulation by the current user, not the original speaker’s consent. No municipal service is contacted.';
export const REFERRAL = 'Consider requesting human assistance through the municipality’s official service channels. This prototype has not contacted or connected you to a representative.';
export const sessionSchema = z.object({
  session_id: z.string(), language_id: languageId, sample_id: z.string(), mode: z.enum(['auto', 'guided']),
  state: z.enum(['select_language', 'ready', 'transcribing', 'confirm', 'accepted', 'retry_or_refer', 'referral']),
  transcript: z.string().nullable(), source: z.enum(['live', 'saved']).nullable(), requested_source: z.enum(['live', 'saved']),
  transcription_status: experimentStatus, attempts: z.number().int().min(0).max(2), max_attempts: z.literal(2),
  retry_available: z.boolean(), retry_sample_ids: z.array(z.string()), confirmation_prompt: z.string().nullable(),
  referral_message: z.string().nullable(), simulation_notice: z.string(), fallback_reason: z.string().nullable(),
  prompt_audio_url: z.string().nullable(), tts_status: z.enum(['cached', 'unavailable']),
  prompt_caption: z.string().nullable().optional(), tts_attribution: z.string().nullable().optional(),
});
export type Session = z.infer<typeof sessionSchema>;
export const capabilitiesSchema = z.object({
  available: z.boolean(), selected_sample_count: z.number().int().nonnegative(), live_configured: z.boolean(),
  languages: z.array(z.object({ language_id: languageId, sample_ids: z.array(z.string()),
    saved_sample_ids_by_mode: z.object({ auto: z.array(z.string()), guided: z.array(z.string()) }), guided_verified: z.boolean() })),
});
export type Capabilities = z.infer<typeof capabilitiesSchema>;

export async function request(path: string, signal: AbortSignal, body?: object): Promise<unknown> {
  const response = await fetch(`${API}/api/recovery/${path}`, { signal,
    ...(body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : {}) });
  const value: unknown = await response.json();
  // Consumed failed attempts carry the usable session even with a non-2xx response.
  if (!response.ok && !(typeof value === 'object' && value !== null && 'error' in value)) throw new Error('Backend unavailable');
  return value;
}

export function offlineAttempt(previous: Session | null, sampleId: string, language: Session['language_id'],
  mode: Session['mode'], samples: Samples, evidence: Experiments): Session {
  const record = evidence.records.find(row => row.sample_id === sampleId && row.language_id === language);
  const outcome = record?.[mode];
  let flags: unknown;
  try { flags = JSON.parse(evidence.source.review_flags ?? '{}'); } catch { flags = null; }
  const flagged = !flags || typeof flags !== 'object' || Array.isArray(flags)
    || Boolean((flags as Record<string, unknown>)[`${sampleId}:${mode}`]
      && (!Array.isArray((flags as Record<string, unknown>)[`${sampleId}:${mode}`])
        || ((flags as Record<string, unknown>)[`${sampleId}:${mode}`] as unknown[]).length));
  const usable = outcome?.status === 'completed' && outcome.cer !== null && Boolean(outcome.transcript_raw?.trim()) && !flagged;
  const attempts = (previous?.attempts ?? 0) + 1;
  const remaining = previous ? previous.retry_sample_ids.filter(id => id !== sampleId)
    : samples.samples.filter(row => row.language_id === language && row.sample_id !== sampleId).map(row => row.sample_id);
  const state = usable ? 'confirm' : attempts >= 2 ? 'referral' : 'retry_or_refer';
  return sessionSchema.parse({ session_id: previous?.session_id ?? `offline-${crypto.randomUUID()}`,
    language_id: language, sample_id: sampleId, mode, state, attempts, max_attempts: 2,
    transcript: usable ? outcome?.transcript_raw : null, source: outcome && outcome.status !== 'not_tested' ? 'saved' : null,
    requested_source: 'saved', transcription_status: flagged && outcome?.status === 'completed' ? 'incompatible_output' : outcome?.status ?? 'not_tested',
    retry_available: state === 'retry_or_refer' && attempts < 2 && remaining.length > 0,
    retry_sample_ids: remaining, confirmation_prompt: usable ? recoveryPrompt(language)?.text ?? null : null,
    referral_message: state === 'referral' || state === 'retry_or_refer' ? REFERRAL : null,
    simulation_notice: NOTICE, fallback_reason: 'Explicit browser-only saved-result simulation',
    prompt_audio_url: null, tts_status: 'unavailable',
  });
}
