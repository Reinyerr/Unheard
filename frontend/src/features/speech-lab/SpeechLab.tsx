import AudioWaveform from '../../components/AudioWaveform';
import EmptyState from '../../components/EmptyState';
import TranscriptDiff from '../../components/TranscriptDiff';
import { useResearch } from '../../data/ResearchData';
import { useSelection } from '../../state/selection';
import type { Outcome, Sample } from '../../types/research';
import { matchingEvidence, percent, useSamples } from './data';
import './speech-lab.css';

function AudioClip({ sample }: { sample: Sample }) {
  return <AudioWaveform src={`${import.meta.env.BASE_URL}${sample.audio_path}`} label={`FLEURS recording ${sample.sample_id}`} />;
}
function Mode({ title, description, outcome, sample, direction, language, flags }: { title: string; description: string; outcome: Outcome | undefined;
  sample: Sample; direction: 'rtl' | 'ltr'; language: string; flags: string[] }) {
  return <section className="speech-mode" aria-label={`${title} transcription`}>
    <h4>{title}</h4>
    <p className="speech-note">{description}</p>
    <dl className="speech-stats"><div><dt>Character error rate</dt><dd>{percent(outcome?.cer ?? null)}</dd></div></dl>
    {outcome && outcome.status !== 'completed' ? <EmptyState kind={outcome.status}>
      {outcome.status === 'incompatible_output' ? 'Output requires script/language review and is excluded from comparable metrics.'
        : outcome.status === 'technical_error' ? 'A provider failure is recorded; this is not a recognition error rate.'
          : outcome.status === 'unsupported' ? 'This setting was unsupported. Automatic mode is not substituted.'
            : 'No attempted outcome is present in the saved artifact.'}
    </EmptyState> : !outcome ? <EmptyState kind="not_tested">No saved outcome for this sample.</EmptyState> : null}
    {flags.length ? <p className="speech-note">Review flags: {flags.join('; ')}</p> : null}
    {outcome?.transcript_raw !== null && outcome?.transcript_raw !== undefined ? <TranscriptDiff reference={sample.reference_transcript} output={outcome.transcript_raw} direction={direction} language={language} /> : <p>No recorded transcript available.</p>}
  </section>;
}
function HintEffect({ difference }: { difference: number | null }) {
  let result = 'Comparison unavailable';
  let detail = 'Both versions need a comparable score for this recording.';
  if (difference !== null) {
    const points = Math.abs(difference * 100);
    const tied = Math.abs(difference) <= 1e-12;
    result = tied ? 'No change in error rate' : difference > 0 ? 'The hint reduced errors' : 'The hint increased errors';
    detail = tied ? '0.0 percentage points on this recording.'
      : `${points < 0.05 ? 'Less than 0.1' : points.toFixed(1)} percentage points ${difference > 0 ? 'lower' : 'higher'} with the hint on this recording.`;
  }
  return <div className="hint-effect">
    <h4>Did the hint help?</h4>
    <p><strong>{result}</strong></p>
    <p>{detail}</p>
  </div>;
}
function reviewFlags(value: string | undefined): Record<string, string[]> {
  try {
    const parsed: unknown = JSON.parse(value ?? '{}');
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter((entry): entry is [string, string[]] => Array.isArray(entry[1]) && entry[1].every(v => typeof v === 'string')));
  } catch { return {}; }
}
export default function SpeechLab() {
  const { selection } = useSelection();
  const { census, experiments, reload } = useResearch();
  const { resource, reload: reloadSamples } = useSamples();
  const samples = resource.status === 'ready' ? resource.data : null;
  const evidence = experiments.status === 'ready' && samples && matchingEvidence(samples, experiments.data) ? experiments.data : null;
  // Feature the same tested FLEURS sentence across the six pilot languages.
  const sample = samples?.samples.find(row => row.language_id === selection.language_id && row.fleurs_id === 1533);
  const record = sample ? evidence?.records.find(row => row.sample_id === sample.sample_id) : undefined;
  if (census.status === 'loading') return <EmptyState kind="loading" />;
  if (census.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>;
  const language = census.data.languages.languages.find(row => row.language_id === selection.language_id);
  if (!language?.pilot_selected) return <EmptyState kind="choose_language">Select a language above to hear its featured recording.</EmptyState>;
  if (resource.status === 'loading') return <EmptyState kind="loading" />;
  if (resource.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reloadSamples}>{resource.message}</EmptyState>;
  if (!sample) return <EmptyState kind="unavailable">The featured recording is unavailable for this language.</EmptyState>;
  const direction = selection.language_id === 'urdu' || selection.language_id === 'arabic' ? 'rtl' : 'ltr';
  const textLanguage = language.dataset_language_code;
  const flags = reviewFlags(evidence?.source.review_flags);
  return <div className="speech-lab">
    {experiments.status === 'loading' ? <EmptyState kind="loading">Loading saved experiment evidence.</EmptyState>
      : experiments.status === 'unavailable' ? <EmptyState kind="unavailable" onRetry={reload}>{experiments.message}</EmptyState>
        : !evidence ? <EmptyState kind="unavailable">Sample identity or selection provenance does not match the experiment artifact. Comparisons are withheld.</EmptyState> : null}
    <section key={sample.sample_id} className="speech-record" aria-label={`Selected recording ${sample.sample_id}`}>
      <AudioClip key={sample.sample_id} sample={sample} />
      <h4 id="speech-reference" tabIndex={-1}>Reference text</h4>
      <p className="speech-transcript" dir={direction} lang={textLanguage}>{sample.raw_reference_transcript}</p>
      <div id="speech-comparisons" className="speech-comparison" tabIndex={-1} role="region" aria-labelledby="speech-comparison-title">
        <h3 id="speech-comparison-title" className="speech-comparison-title">Comparison</h3>
        {evidence ? <>
          <HintEffect difference={record?.paired_delta_cer ?? null} />
          <div className="speech-modes">
            <Mode title="Without a language hint" description="The model works out the language on its own." outcome={record?.auto}
              sample={sample} direction={direction} language={textLanguage} flags={flags[`${sample.sample_id}:auto`] ?? []} />
            <Mode title="With a language hint" description={record?.guided.language_hint
              ? `Language hint: ${language.display_name} (${record.guided.language_hint}).` : 'This mode gives the model the language upfront.'}
              outcome={record?.guided} sample={sample} direction={direction} language={textLanguage} flags={flags[`${sample.sample_id}:guided`] ?? []} />
          </div>
        </> : <p>Saved comparisons are unavailable; the reference and authentic audio remain independent.</p>}
      </div>
      <a className="speech-note" href={`${import.meta.env.BASE_URL}audio/FLEURS_ATTRIBUTION.txt`}>Recording credits</a>
    </section>
  </div>;
}
