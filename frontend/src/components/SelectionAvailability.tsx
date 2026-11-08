import { useResearch } from '../data/ResearchData';
import { useSelection } from '../state/selection';
import type { ExperimentStatus } from '../types/research';
import EmptyState, { statusLabels } from './EmptyState';

/** Language-level eligibility/empty states only; playback, recovery controls and ranking views are later tickets. */
export default function SelectionAvailability({ module }: { module: 'investigate' | 'demonstrate' | 'recommend' }) {
  const { selection } = useSelection();
  const { census, experiments, recommendations, reload } = useResearch();
  if (census.status === 'loading') return <EmptyState kind="loading" />;
  if (census.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>;
  if (selection.language_id === 'all') return <EmptyState kind="choose_language">Select one language above to see this module's eligibility and evidence availability.</EmptyState>;
  const language = census.data.languages.languages.find(row => row.language_id === selection.language_id);
  if (!language) return <EmptyState kind="unavailable">This language is unavailable in the loaded coverage data.</EmptyState>;
  if (module === 'demonstrate') return <EmptyState kind="pending" title={`${language.display_name} confirmation demo`}>
    Confirmation controls are not available in this view yet. Language guidance and voice capabilities are reported only after verification.
  </EmptyState>;
  if (module === 'recommend') {
    if (recommendations.status === 'loading') return <EmptyState kind="loading" />;
    if (recommendations.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{recommendations.message}</EmptyState>;
    const item = recommendations.data.items.find(row => row.language_id === language.language_id);
    return <EmptyState kind="pending" title={`${language.display_name} recommendation context`}>
      {item ? 'A supplied coverage-gap research recommendation is available for this language.'
        : language.coverage_status === 'has_task_audio'
          ? 'Task-request audio is present in the supplied subsets. This language is not ranked as an unmeasured category.'
          : 'No recommendation is present in the supplied artifact for this language.'}
      {' '}Full recommendation details are not yet available in this view.
    </EmptyState>;
  }
  if (!language.pilot_selected) return <EmptyState kind="not_tested" title={`${language.display_name}: Not tested`}>
    This language is outside the selected six-language pilot. Demographic coverage remains available independently.
  </EmptyState>;
  if (experiments.status === 'loading') return <EmptyState kind="loading" />;
  if (experiments.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{experiments.message}</EmptyState>;
  const records = experiments.data.records.filter(row => row.language_id === language.language_id);
  const counts = new Map<ExperimentStatus, number>();
  for (const record of records) for (const outcome of [record.auto, record.guided]) counts.set(outcome.status, (counts.get(outcome.status) ?? 0) + 1);
  if (!records.length || [...counts.keys()].every(status => status === 'not_tested')) return <EmptyState kind="not_tested" title={`${language.display_name}: Not tested`}>
    Selected for the pilot; no attempted recording outcome is present in the saved artifact. No error-rate metric is available.
  </EmptyState>;
  return <div className="selection-evidence" aria-live="polite">
    <h3>{language.display_name}: saved evidence status</h3>
    <p>Recorded automatic and guided outcomes across {records.length} selected clips. These recordings have no ward-residency assignment.</p>
    <dl>{[...counts].map(([status, count]) => <div key={status}><dt>{statusLabels[status]}</dt><dd>{count} recording modes</dd></div>)}</dl>
    {[...counts.keys()].filter(status => ['unsupported', 'technical_error', 'incompatible_output'].includes(status)).map(status =>
      <EmptyState key={status} kind={status}>{status === 'unsupported' ? 'The recorded setting was unsupported; no numeric result is substituted.'
        : status === 'technical_error' ? 'A recorded provider failure is preserved separately from transcription quality.'
          : 'Flagged output is excluded from comparable metrics until reviewed.'}</EmptyState>)}
    <p>Playback and comparison controls are not yet available in this view. No transcript or error rate is inferred from selection.</p>
  </div>;
}
