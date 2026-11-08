import { useEffect } from 'react';
import AudioWaveform from '../../components/AudioWaveform';
import EmptyState, { statusLabels } from '../../components/EmptyState';
import TranscriptDiff from '../../components/TranscriptDiff';
import { useResearch } from '../../data/ResearchData';
import { useSelection } from '../../state/selection';
import type { Outcome, Sample } from '../../types/research';
import { delta, matchingEvidence, percent, useSamples } from './data';
import './speech-lab.css';

function AudioClip({ sample }: { sample: Sample }) {
  return <AudioWaveform src={`${import.meta.env.BASE_URL}${sample.audio_path}`} label={`FLEURS recording ${sample.sample_id}`} />;
}
function Mode({ title, outcome, sample, direction, language, flags }: { title: string; outcome: Outcome | undefined;
  sample: Sample; direction: 'rtl' | 'ltr'; language: string; flags: string[] }) {
  return <section className="speech-mode" aria-label={`${title} transcription`}>
    <h4>{title}</h4>
    <p><strong>{outcome ? statusLabels[outcome.status] : 'Not tested'}</strong>{outcome?.status === 'completed' ? ' · Saved provider output' : ''}</p>
    {outcome?.language_hint ? <p>Recorded language hint: <bdi>{outcome.language_hint}</bdi></p> : null}
    {outcome && outcome.status !== 'completed' ? <EmptyState kind={outcome.status}>
      {outcome.status === 'incompatible_output' ? 'Output requires script/language review and is excluded from comparable metrics.'
        : outcome.status === 'technical_error' ? 'A provider failure is recorded; this is not a recognition error rate.'
          : outcome.status === 'unsupported' ? 'This setting was unsupported. Automatic mode is not substituted.'
            : 'No attempted outcome is present in the saved artifact.'}
    </EmptyState> : !outcome ? <EmptyState kind="not_tested">No saved outcome for this sample.</EmptyState> : null}
    {flags.length ? <p className="speech-note">Review flags: {flags.join('; ')}</p> : null}
    <dl className="speech-stats"><div><dt>CER</dt><dd>{percent(outcome?.cer ?? null)}</dd></div></dl>
    {outcome?.transcript_raw !== null && outcome?.transcript_raw !== undefined ? <TranscriptDiff reference={sample.reference_transcript} output={outcome.transcript_raw} direction={direction} language={language} /> : <p>No recorded transcript available.</p>}
  </section>;
}
function reviewFlags(value: string | undefined): Record<string, string[]> {
  try {
    const parsed: unknown = JSON.parse(value ?? '{}');
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter((entry): entry is [string, string[]] => Array.isArray(entry[1]) && entry[1].every(v => typeof v === 'string')));
  } catch { return {}; }
}
export default function SpeechLab() {
  const { selection, selectSample, acceptResult } = useSelection();
  const { census, experiments, reload } = useResearch();
  const { resource, reload: reloadSamples } = useSamples();
  const samples = resource.status === 'ready' ? resource.data : null;
  const evidence = experiments.status === 'ready' && samples && matchingEvidence(samples, experiments.data) ? experiments.data : null;
  const choices = samples?.samples.filter(sample => sample.language_id === selection.language_id) ?? [];
  const sample = choices.find(row => row.sample_id === selection.selected_sample?.sample_id);
  const record = sample ? evidence?.records.find(row => row.sample_id === sample.sample_id) : undefined;
  useEffect(() => {
    // The render also gates by current language/sample: no previous comparison can flash before this effect.
    if (selection.selected_result?.sample_id !== record?.sample_id) acceptResult(record ?? null, selection.language_revision);
  }, [record, selection.selected_result, selection.language_revision, acceptResult]);
  if (census.status === 'loading') return <EmptyState kind="loading" />;
  if (census.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>;
  if (selection.language_id === 'all') return <EmptyState kind="choose_language">Select a pilot language above to inspect its frozen sample manifest.</EmptyState>;
  const language = census.data.languages.languages.find(row => row.language_id === selection.language_id);
  if (!language?.pilot_selected) return <EmptyState kind="not_tested">{language?.display_name ?? 'This language'} is outside the six-language pilot. No recognition metric is inferred.</EmptyState>;
  if (resource.status === 'loading') return <EmptyState kind="loading" />;
  if (resource.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reloadSamples}>{resource.message}</EmptyState>;
  if (!samples || !choices.length) return <EmptyState kind="unavailable">No vetted samples are available for this language.</EmptyState>;
  const summary = evidence?.summaries.find(row => row.language_id === selection.language_id);
  const scoredClipCount = evidence?.records.filter(row => row.language_id === selection.language_id
    && (row.auto.cer !== null || row.guided.cer !== null)).length ?? 0;
  const direction = selection.language_id === 'urdu' || selection.language_id === 'arabic' ? 'rtl' : 'ltr';
  const textLanguage = language.dataset_language_code;
  const flags = reviewFlags(evidence?.source.review_flags);
  return <div className="speech-lab">
    <p><strong>Saved research evidence · no live transcription requests</strong></p>

    <p>{choices.length} selected {language.display_name} clips · {samples.samples.length} total · seed {samples.selection.seed}. {summary ? `Scored automatic n=${summary.n_auto_completed}; guided n=${summary.n_guided_completed}; paired n=${summary.n_paired}.` : 'Summary unavailable.'}</p>
    <label htmlFor="speech-sample">Recording
      <select id="speech-sample" value={sample?.sample_id ?? ''} onChange={event => selectSample(choices.find(row => row.sample_id === event.target.value) ?? null, selection.language_revision)}>
        <option value="">Choose a recording</option>
        {choices.map(row => <option key={row.sample_id} value={row.sample_id}>{row.sample_id} · {row.duration_sec === null ? 'duration unavailable' : `${row.duration_sec.toFixed(2)} s`}</option>)}
      </select>
    </label>
    {experiments.status === 'loading' ? <EmptyState kind="loading">Loading saved experiment evidence.</EmptyState>
      : experiments.status === 'unavailable' ? <EmptyState kind="unavailable" onRetry={reload}>{experiments.message}</EmptyState>
        : !evidence ? <EmptyState kind="unavailable">Sample identity or selection provenance does not match the experiment artifact. Comparisons are withheld.</EmptyState> : null}
    {sample ? <section key={sample.sample_id} className="speech-record" aria-label={`Selected recording ${sample.sample_id}`}>
      <h3><bdi>{sample.sample_id}</bdi> · FLEURS ID {sample.fleurs_id}</h3>
      <AudioClip key={sample.sample_id} sample={sample} />
      <nav className="transcript-navigation" aria-label="Selected recording text"><a href="#speech-reference">Read reference transcript</a><a href="#speech-comparisons">Compare saved transcriptions</a></nav>
      <h4 id="speech-reference" tabIndex={-1}>Human reference · original supplied text</h4>
      <p className="speech-transcript" dir={direction} lang={textLanguage}>{sample.raw_reference_transcript}</p>
      {sample.reference_transcript !== sample.raw_reference_transcript ? <details><summary>Supplied reference used as metric input</summary><p className="speech-transcript" dir={direction} lang={textLanguage}>{sample.reference_transcript}</p></details> : null}
      <p>Clip paired CER delta: <strong>{delta(record?.paired_delta_cer ?? null)}</strong></p>
      {record?.provenance.evaluated_at_utc ? <p className="speech-note">Saved evaluation: {record.provenance.evaluated_at_utc} · source: {record.provenance.source_dataset}</p> : null}
      <div id="speech-comparisons" tabIndex={-1} role="region" aria-label="Saved transcription comparisons">
        {evidence ? <div className="speech-modes"><Mode title="Automatic detection" outcome={record?.auto} sample={sample} direction={direction} language={textLanguage} flags={flags[`${sample.sample_id}:auto`] ?? []} /><Mode title="Guided language" outcome={record?.guided} sample={sample} direction={direction} language={textLanguage} flags={flags[`${sample.sample_id}:guided`] ?? []} /></div> : <p>Saved comparisons are unavailable; the reference and authentic audio remain independent.</p>}
      </div>
    </section> : <EmptyState kind="pending" title="Choose a recording">The complete frozen selection is available above; no clip is chosen based on its outcome.</EmptyState>}
    <details className="metric-explainer"><summary>How to read the comparison · CER is lower-is-better</summary><p className="speech-note">Character error rate (CER) compares text edits with reference characters; lower is better and insertions can exceed 100%. CER does not measure whether a municipal request was understood.</p></details>
    {summary ? <details aria-label="Language pilot summary" className="speech-summary"><summary>Language pilot summary · sample counts and limitations</summary>
      <h3>{language.display_name} pilot summary</h3>
      {scoredClipCount === 1 ? <p><strong>One-recording demonstration.</strong> These results cover one recording, not overall performance for this language.</p> : null}
      <p>Selected n={summary.n_selected}; scored automatic n={summary.n_auto_completed}; scored guided n={summary.n_guided_completed}; comparable pairs n={summary.n_paired}.</p>
      <dl className="speech-stats"><div><dt>Mean automatic CER</dt><dd>{percent(summary.mean_auto_cer)}</dd></div><div><dt>Mean guided CER</dt><dd>{percent(summary.mean_guided_cer)}</dd></div><div><dt>Mean paired delta</dt><dd>{delta(summary.mean_delta_cer)}</dd></div></dl>
      <p>Improved {summary.improved_count} · worsened {summary.worsened_count} · tied {summary.unchanged_count} (comparable pairs only).</p>
      {Object.keys(summary.unpaired_reasons).length ? <p>Unpaired reasons (clip/status counts may overlap): {Object.entries(summary.unpaired_reasons).map(([status, count]) => `${status}: ${count}`).join('; ')}.</p> : null}
      <p className="speech-note">Positive delta = automatic CER minus guided CER, so lower guided error; negative means worse. Mode means can use different clips. Tiny partial exploratory sample; no significance, population or ward-level inference.</p>
    </details> : evidence ? <EmptyState kind="unavailable">No exported language summary is available.</EmptyState> : null}
    <details className="speech-sources"><summary>Speech sources, model and metric policy</summary>
      <p>{samples.source.attribution}. <a href="https://huggingface.co/datasets/google/fleurs">FLEURS source</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
      <p>{samples.source.modifications}</p><p>{samples.source.limitations}</p>
      <p>Common FLEURS IDs: {samples.selection.ids.join(', ')}.</p>
      <p>Manifest exported: {samples.generated_at_utc} · selection SHA-256: <span className="speech-hash">{samples.source.selection_sha256}</span></p>
      {evidence ? <><p>Provider {evidence.model.provider} · model {evidence.model.model_id ?? 'unavailable'} · API {evidence.model.api_version ?? 'unavailable'} · results exported {evidence.generated_at_utc}. Provider model-alias weight revisions are unknown.</p>
        <p>{evidence.source.normalization}</p><p>{evidence.source.cer_units}</p><p>{evidence.source.script_policy}</p><p>{evidence.source.limitations}</p></> : null}
      <p>Curated local audio only; public-package attribution/licence audit remains pending. FLEURS recordings are not municipal requests and have no identified Mississauga ward residency.</p>
    </details>
  </div>;
}
