import { z } from 'zod';
import mapping from '../../../shared/language_map.json';

export type LanguageId = keyof typeof mapping.languages;
export const languageMap = mapping.languages;
export const languageId = z.enum(Object.keys(languageMap) as [LanguageId, ...LanguageId[]]);
export function languageIdForName(name: string): LanguageId {
  const id = (Object.keys(languageMap) as LanguageId[]).find(key => languageMap[key].display_name === name);
  if (!id) throw new Error(`Unknown source language: ${name}`);
  return id;
}
export const coverageStatus = z.enum(['no_task_audio', 'has_task_audio']);
export const experimentStatus = z.enum(['not_tested', 'completed', 'technical_error', 'unsupported', 'incompatible_output']);
export const recoveryState = z.enum(['select_language', 'ready', 'transcribing', 'confirm', 'accepted', 'retry_or_refer', 'referral']);
export const origin = z.enum(['live', 'saved']);
export const mapMetric = z.enum(['count', 'share']);
export type CoverageStatus = z.infer<typeof coverageStatus>;
export type ExperimentStatus = z.infer<typeof experimentStatus>;
export type RecoveryState = z.infer<typeof recoveryState>;
export type Origin = z.infer<typeof origin>;
export type MapMetric = z.infer<typeof mapMetric>;

const count = z.number().int().nonnegative();
const wardId = count.min(1).max(11);
const ratio = z.number().finite().nonnegative(); // CER may exceed 1.
const number = z.number().finite();
const text = z.string();
const nullableText = text.nullable();
const object = <S extends z.ZodRawShape>(shape: S) => z.object(shape).strict();
const fail = (ctx: z.RefinementCtx, message: string) => ctx.addIssue({ code: 'custom', message });
function distinct<T extends z.ZodType>(schema: T, key: (value: z.infer<T>) => unknown) {
  return z.array(schema).superRefine((rows, ctx) => {
    if (new Set(rows.map(key)).size !== rows.length) fail(ctx, 'Duplicate identifier');
  });
}
const header = {
  schema_version: z.literal('1.0'),
  generated_at_utc: text.datetime({ offset: true }).refine(v => v.endsWith('Z') || v.endsWith('+00:00'), 'Expected UTC timestamp').nullable(),
  source: z.record(text, text).refine(v => Object.keys(v).length > 0, 'Source provenance is required'),
  is_fixture: z.boolean().default(false),
  fixture_label: nullableText.default(null),
};
function artifact<S extends z.ZodRawShape>(shape: S) {
  return object({ ...header, ...shape }).superRefine((data, ctx) => {
    // Header fields are shared by every artifact; fixture opt-in is enforced by the loader below.
    const value = data as { is_fixture: boolean; fixture_label: string | null; generated_at_utc: string | null };
    if (value.is_fixture && !value.fixture_label?.startsWith('MOCK')) fail(ctx, 'Fixtures require an explicit MOCK label');
    if (!value.is_fixture && value.generated_at_utc === null) fail(ctx, 'Research artifacts require generation time');
  });
}

export const languageSchema = object({
  language_id: languageId, display_name: text, census_home_column: nullableText,
  city_home_speakers: count.nullable(), coverage_status: coverageStatus,
  request_clip_counts: object({ minds14: count, speech_massive: count }),
  fleurs_config: nullableText, dataset_language_code: text, pilot_selected: z.boolean(),
}).superRefine((row, ctx) => {
  const expected = languageMap[row.language_id];
  for (const key of ['display_name', 'census_home_column', 'fleurs_config', 'dataset_language_code'] as const) {
    if (row[key] !== expected[key]) fail(ctx, `${row.language_id}: incorrect ${key}`);
  }
  if ((row.request_clip_counts.minds14 + row.request_clip_counts.speech_massive > 0) !== (row.coverage_status === 'has_task_audio')) fail(ctx, 'Coverage status disagrees with counts');
});
export const languagesSchema = artifact({ languages: distinct(languageSchema, r => r.language_id) });

export const wardSchema = object({
  ward_id: wardId, population_language_base: count.nullable(), gap_population: count.nullable(),
  gap_share_pct: ratio.max(100).nullable(), home_speakers_by_language: z.partialRecord(languageId, count.nullable()),
}).superRefine((row, ctx) => {
  const expected = row.population_language_base && row.gap_population !== null ? 100 * row.gap_population / row.population_language_base : null;
  if (expected === null ? row.gap_share_pct !== null : row.gap_share_pct === null || Math.abs(expected - row.gap_share_pct) > 1e-6) fail(ctx, 'Ward share disagrees with denominator/count');
});
export const wardsSchema = artifact({
  source_file: z.literal('01_people_census/derived/ward_language_profile_2021_corrected.csv'),
  missing_request_language_ids: distinct(languageId, id => id), wards: distinct(wardSchema, r => r.ward_id),
});

const identity = { sample_id: text, language_id: languageId, fleurs_id: count };
function checkIdentity(row: { sample_id: string; language_id: LanguageId; fleurs_id: number }, ctx: z.RefinementCtx) {
  if (row.sample_id !== `${row.language_id}-${row.fleurs_id}`) fail(ctx, 'sample_id must match language_id and fleurs_id');
}
export const sampleSchema = object({
  ...identity,
  audio_path: text.refine(v => v.startsWith('audio/') && !v.includes('\\') && !v.includes(':') && v.split('/').every(p => p !== '' && p !== '.' && p !== '..'), 'Expected relative audio/ asset path'),
  raw_reference_transcript: text, reference_transcript: text,
  gender: z.enum(['female', 'male', 'other']), duration_sec: ratio.positive().nullable(),
}).superRefine(checkIdentity);
export const samplesSchema = artifact({
  selection: object({ seed: z.literal(2026), strategy: z.literal('common_fleurs_ids_random_sample'),
    ids: distinct(count, id => id).refine(ids => ids.every((id, i) => i === 0 || ids[i - 1] < id), 'Selection IDs must be sorted') }),
  samples: distinct(sampleSchema, r => r.sample_id),
}).superRefine((data, ctx) => {
  if (data.samples.some(row => !data.selection.ids.includes(row.fleurs_id))) fail(ctx, 'Sample ID is absent from selection');
});

export const outcomeSchema = object({
  status: experimentStatus, transcript_raw: nullableText, cer: ratio.nullable(), wer: ratio.nullable(),
  request_id: nullableText, language_hint: nullableText.default(null),
}).superRefine((row, ctx) => {
  if (row.status !== 'completed' && (row.cer !== null || row.wer !== null)) fail(ctx, 'Non-completed outcomes must have null CER/WER');
});
export const experimentSchema = object({
  ...identity, auto: outcomeSchema, guided: outcomeSchema, paired_delta_cer: number.nullable(),
  provenance: object({ source_dataset: text, evaluated_at_utc: nullableText }),
}).superRefine((row, ctx) => {
  checkIdentity(row, ctx);
  const expected = row.auto.cer !== null && row.guided.cer !== null ? row.auto.cer - row.guided.cer : null;
  if (expected === null ? row.paired_delta_cer !== null : row.paired_delta_cer === null || Math.abs(expected - row.paired_delta_cer) > 1e-9) fail(ctx, 'Invalid paired CER delta');
});
export const summarySchema = object({
  language_id: languageId, n_selected: count, n_auto_completed: count, n_guided_completed: count, n_paired: count,
  mean_auto_cer: ratio.nullable(), mean_guided_cer: ratio.nullable(), mean_delta_cer: number.nullable(),
  improved_count: count, worsened_count: count, unchanged_count: count,
  unpaired_reasons: z.partialRecord(experimentStatus, count),
}).superRefine((row, ctx) => {
  if (row.n_paired > Math.min(row.n_auto_completed, row.n_guided_completed)
    || Math.max(row.n_auto_completed, row.n_guided_completed) > row.n_selected
    || row.improved_count + row.worsened_count + row.unchanged_count !== row.n_paired) fail(ctx, 'Inconsistent summary counts');
  if ((row.n_auto_completed === 0 && row.mean_auto_cer !== null)
    || (row.n_guided_completed === 0 && row.mean_guided_cer !== null)
    || (row.n_paired === 0 && row.mean_delta_cer !== null)) fail(ctx, 'Empty summary requires null metric');
});
export const experimentsSchema = artifact({
  model: object({ provider: z.literal('elevenlabs'), model_id: nullableText, api_version: nullableText }),
  records: distinct(experimentSchema, r => r.sample_id), summaries: distinct(summarySchema, r => r.language_id),
});
export const recommendationSchema = object({
  language_id: languageId, reason: text, city_home_speakers: count, rank: count.min(1),
  suggested_action: text, suggested_ward_ids: distinct(wardId, id => id), limitations: z.array(text),
});
export const recommendationsSchema = artifact({
  method: z.literal('missing_task_audio_then_city_home_speakers_desc'), items: distinct(recommendationSchema, r => r.language_id),
}).superRefine((data, ctx) => {
  if (new Set(data.items.map(r => r.rank)).size !== data.items.length) fail(ctx, 'Duplicate recommendation rank');
});

export const artifactSchemas = { languages: languagesSchema, wards: wardsSchema, samples: samplesSchema,
  experiments: experimentsSchema, recommendations: recommendationsSchema };
export type ArtifactKind = keyof typeof artifactSchemas;
export type Languages = z.infer<typeof languagesSchema>;
export type Wards = z.infer<typeof wardsSchema>;
export type Samples = z.infer<typeof samplesSchema>;
export type Experiments = z.infer<typeof experimentsSchema>;
export type Recommendations = z.infer<typeof recommendationsSchema>;
export type Language = z.infer<typeof languageSchema>;
export type Ward = z.infer<typeof wardSchema>;
export type Sample = z.infer<typeof sampleSchema>;
export type Outcome = z.infer<typeof outcomeSchema>;
export type Experiment = z.infer<typeof experimentSchema>;
export type Summary = z.infer<typeof summarySchema>;
export type Recommendation = z.infer<typeof recommendationSchema>;

export function validateArtifact<K extends ArtifactKind>(kind: K, data: unknown, allowFixtures = false): z.infer<(typeof artifactSchemas)[K]> {
  const result = artifactSchemas[kind].parse(data);
  if (result.is_fixture && !allowFixtures) throw new Error('MOCK fixture cannot be loaded as research data');
  return result as z.infer<(typeof artifactSchemas)[K]>;
}
export function validateBundle(input: unknown, allowFixtures = false) {
  const data = object(artifactSchemas).parse(input);
  for (const kind of Object.keys(artifactSchemas) as ArtifactKind[]) validateArtifact(kind, data[kind], allowFixtures);
  const languages = new Set(data.languages.languages.map(r => r.language_id));
  const wards = new Set(data.wards.wards.map(r => r.ward_id));
  const samples = new Set(data.samples.samples.map(r => r.sample_id));
  const referenced: string[] = [...data.wards.missing_request_language_ids,
    ...data.wards.wards.flatMap(r => Object.keys(r.home_speakers_by_language)),
    ...data.samples.samples.map(r => r.language_id), ...data.experiments.records.map(r => r.language_id),
    ...data.experiments.summaries.map(r => r.language_id), ...data.recommendations.items.map(r => r.language_id)];
  if (referenced.some(id => !languages.has(id as LanguageId))) throw new Error('Language reference absent from languages artifact');
  if (data.experiments.records.some(r => !samples.has(r.sample_id))) throw new Error('Experiment references missing sample');
  if (data.recommendations.items.some(r => r.suggested_ward_ids.some(id => !wards.has(id)))) throw new Error('Recommendation references missing ward');
  return data;
}
