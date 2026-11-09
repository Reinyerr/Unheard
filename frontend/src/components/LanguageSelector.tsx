import { useResearch } from '../data/ResearchData';
import { useSelection } from '../state/selection';
import EmptyState from './EmptyState';

export default function LanguageSelector({ pilotOnly = false }: { pilotOnly?: boolean }) {
  const { census, reload } = useResearch();
  const { selection, selectLanguage, reset, dismissError } = useSelection();
  const languages = census.status === 'ready'
    ? census.data.languages.languages.filter(language => !pilotOnly || language.pilot_selected)
    : [];
  const value = pilotOnly && !languages.some(language => language.language_id === selection.language_id)
    ? ''
    : selection.language_id;
  return <section id="language-selection" tabIndex={-1} className="global-selection" aria-label="Explore a language">
    {census.status === 'ready' ? <label htmlFor="global-language">Selected language
      <select id="global-language" value={value} onChange={event => selectLanguage(event.target.value)}>
        {pilotOnly ? <option value="" disabled>Choose a language</option> : <option value="all">All tracked languages</option>}
        {languages.map(language => <option key={language.language_id} value={language.language_id}>{language.display_name}</option>)}
      </select>
    </label> : census.status === 'loading' ? <EmptyState kind="loading" />
      : <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>}
    <button type="button" onClick={reset}>Reset selection</button>
    {selection.error ? <EmptyState kind="unavailable" title="Selection corrected" onRetry={dismissError} retryLabel="Dismiss notice">{selection.error}</EmptyState> : null}
  </section>;
}
