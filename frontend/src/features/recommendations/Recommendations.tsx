import EmptyState from '../../components/EmptyState';
import PriorityTable from '../../components/PriorityTable';
import { useResearch } from '../../data/ResearchData';
import { useSelection } from '../../state/selection';
import { formatCount, formatShare } from '../map/metrics';
import type { Language, MapMetric, Wards } from '../../types/research';
import { rankedWards, rankingError } from './ranking';
import './recommendations.css';

function WardPriorities({ wards, language, metric, onSelect }: { wards: Wards; language: Language; metric: MapMetric; onSelect: (id: number) => void }) {
  const rows = rankedWards(wards, language.language_id, metric).slice(0, 3);
  return <section className="recommendation-ward-list" aria-label={`Top wards by ${metric}`}>
    <h4>{metric === 'count' ? 'Most home-language speakers' : 'Highest home-language share'}</h4>
    <p>{metric === 'count' ? 'Recruitment volume: count descending.' : 'Concentration: unrounded count ÷ population_language_base descending.'} Equal values use ascending ward ID.</p>
    {rows.length ? <div className="priority-table-scroll" role="region" tabIndex={0} aria-label={`Scrollable top wards by ${metric}`}><table className="priority-table">
      <caption>{language.display_name} · top {rows.length} wards by {metric}</caption>
      <thead><tr><th scope="col">Ward</th><th scope="col">Home speakers</th><th scope="col">Share</th><th scope="col">Language base</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.ward_id}><th scope="row"><a href="#discover" onClick={() => onSelect(row.ward_id)}>Ward {row.ward_id}</a></th><td>{formatCount(row.count)}</td><td>{formatShare(row.share)}</td><td>{formatCount(row.base)}</td></tr>)}</tbody>
    </table></div> : <EmptyState kind="unavailable">No eligible ward values are available for this ranking.</EmptyState>}
    <p className="recommendation-note">Unavailable {metric === 'share' ? 'counts or nonpositive/missing denominators' : 'counts'} are excluded. Ward links open census context only.</p>
  </section>;
}
function PilotEvidence({ language }: { language: Language }) {
  const { experiments, reload } = useResearch();
  const percent = (value: number | null) => value === null ? 'Not available' : `${(value * 100).toFixed(1)}%`;
  if (!language.pilot_selected) return <EmptyState kind="not_tested">{language.display_name} is outside the six-language FLEURS pilot. Coverage priorities do not imply provider failure.</EmptyState>;
  if (experiments.status === 'loading') return <EmptyState kind="loading" />;
  if (experiments.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{experiments.message} Coverage ranking remains independent.</EmptyState>;
  const summary = experiments.data.summaries.find(row => row.language_id === language.language_id);
  if (!summary) return <EmptyState kind="not_tested">No exported pilot summary is present for {language.display_name}.</EmptyState>;
  return <>
    {summary.n_auto_completed === 0 && summary.n_guided_completed === 0 ? <EmptyState kind={Object.keys(summary.unpaired_reasons).every(status => status === 'not_tested') ? 'not_tested' : 'pending'} title="No comparable scored outcomes">No comparable scored pilot outcomes are available for {language.display_name}. Recorded exclusions, if any, remain below.</EmptyState> : null}
    <p>Saved FLEURS pilot · selected n={summary.n_selected}; scored automatic n={summary.n_auto_completed}; scored guided n={summary.n_guided_completed}; comparable pairs n={summary.n_paired}.</p>
    <dl className="recommendation-evidence-stats"><div><dt>Mean automatic CER</dt><dd>{percent(summary.mean_auto_cer)}</dd></div><div><dt>Mean guided CER</dt><dd>{percent(summary.mean_guided_cer)}</dd></div><div><dt>Mean paired delta (auto − guided)</dt><dd>{summary.mean_delta_cer === null ? 'Not available' : `${summary.mean_delta_cer > 0 ? '+' : ''}${(summary.mean_delta_cer * 100).toFixed(1)} percentage points`}</dd></div></dl>
    <p>Comparable pairs: improved {summary.improved_count}, worsened {summary.worsened_count}, tied {summary.unchanged_count}. {Object.entries(summary.unpaired_reasons).map(([status, n]) => `${status}: ${n}`).join('; ')}</p>
    <p className="recommendation-note">Provider {experiments.data.model.provider} · {experiments.data.model.model_id ?? 'model unavailable'} · API {experiments.data.model.api_version ?? 'unavailable'}. Exported {experiments.data.generated_at_utc}. Positive paired delta means lower guided CER. Mode means may use different clips; this small partial pilot supports no significance or local population claim.</p>
    <a href="#investigate">Inspect recordings, raw outcomes, review flags and metric policy</a>
  </>;
}
export default function Recommendations() {
  const { census, recommendations, reload } = useResearch();
  const { selection, selectLanguage, selectWard } = useSelection();
  if (census.status === 'loading' || recommendations.status === 'loading') return <EmptyState kind="loading" />;
  if (census.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>;
  if (recommendations.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{recommendations.message}</EmptyState>;
  const { wards, languages } = census.data;
  const data = recommendations.data;
  const error = rankingError(data, languages, wards);
  if (error) return <EmptyState kind="unavailable" onRetry={reload}>{error} Rankings are withheld.</EmptyState>;
  const language = languages.languages.find(row => row.language_id === selection.language_id);
  const item = data.items.find(row => row.language_id === selection.language_id);
  const gapCount = data.items.reduce((total, row) => total + row.city_home_speakers, 0);
  const tracked = languages.languages.filter(row => row.census_home_column !== null);
  const trackedCount = tracked.every(row => row.city_home_speakers !== null) ? tracked.reduce((total, row) => total + (row.city_home_speakers ?? 0), 0) : null;
  return <div className="recommendations">
    <h3>Language evidence gaps first</h3>
    <p>{data.items.length} tracked categories have no labelled task-request recordings in the supplied MInDS-14 and Speech-MASSIVE subsets: {formatCount(gapCount)} home-language speakers out of {formatCount(trackedCount)} across {tracked.length} tracked non-official categories{trackedCount ? ` (${(100 * gapCount / trackedCount).toFixed(1)}%)` : ''}. This denominator is not the city population.</p>
    <p>Priorities use missing supplied coverage, then city home-language counts descending; equal counts use canonical language ID. CER never changes this order. Coverage is an evidence gap, not a forecast of recognition failure or a measure of English ability.</p>
    <PriorityTable data={data} languages={languages} selected={selection.language_id} onSelect={selectLanguage} />
    {language ? <section className="recommendation-detail" aria-label="Selected language research plan">
      <h3>{language.display_name}: {item ? `evaluation priority ${item.rank}` : 'covered in supplied task subsets'}</h3>
      <p>{item ? item.reason : 'Task-request audio is present in the supplied subsets. This language is not in the missing-coverage ranking; supplied coverage does not establish sufficient evaluation.'}</p>
      <p>City home-language count: {formatCount(language.city_home_speakers)} · supplied MInDS-14 clips: {formatCount(language.request_clip_counts.minds14)} · Speech-MASSIVE clips: {formatCount(language.request_clip_counts.speech_massive)}.</p>
      <h4>Plan task-specific evaluation</h4>
      <p>{item?.suggested_action ?? `Review existing ${language.display_name} task evidence with community partners; collect consented realistic municipal-request recordings where coverage is insufficient.`}</p>
      <p>Include varied dialects and willing speakers, document consent and sampling limits, then validate confirmation, retry and human-assistance referral safeguards before any service use. No municipal request is executed here.</p>
      <h4>Ward context for future recruitment</h4>
      <p>Count and share are independent views of corrected 2021 census categories. Share uses population_language_base. No polygons are required for these tables; geography describes recruitment context, never the location or recognition performance of FLEURS speakers.</p>
      <div className="recommendation-wards"><WardPriorities wards={wards} language={language} metric="count" onSelect={selectWard} /><WardPriorities wards={wards} language={language} metric="share" onSelect={selectWard} /></div>
      {item ? <details><summary>Recommendation limitations</summary><ul>{item.limitations.map(text => <li key={text}>{text}</li>)}</ul></details> : null}
      <section className="recommendation-pilot" aria-label="Separate experimental evidence"><h3>Separate experimental evidence · {language.display_name}</h3><p>These saved exploratory results do not contribute to language or ward ranks. FLEURS is read speech, not local municipal requests; speakers have no identified Mississauga ward residency.</p><PilotEvidence language={language} /></section>
    </section> : <EmptyState kind="choose_language">Choose a priority language in the table or use the global selector to view its ward context and separate pilot evidence.</EmptyState>}
    <details className="recommendation-sources"><summary>Sources and ranking provenance</summary>
      <p>{data.source.attribution}. {data.source.task_dataset_attribution}.</p>
      <p>{wards.source_file} · {wards.wards.length} wards · {languages.languages.length} coverage/crosswalk categories · {data.items.length} recommendations. Exported {data.generated_at_utc}.</p>
      <p>{data.source.ranking_policy}. {data.source.ward_selection_policy}. {data.source.ward_export_policy}.</p>
      <p>{data.source.license}. {data.source.task_dataset_licenses}.</p>
      <p>Corrected census SHA-256: <span>{data.source[`${wards.source_file}:sha256`]}</span></p>
      <p>2021 home-language categories do not establish individual need, service demand or English ability. Non-local speech, script and speaker limitations prevent resident-level inference. No combined demographic/error score is used.</p>
    </details>
  </div>;
}
