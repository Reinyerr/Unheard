import { useResearch } from '../data/ResearchData';
import { useSelection } from '../state/selection';
import EmptyState from './EmptyState';

export default function LanguageSelector() {
  const { census, reload } = useResearch();
  const { selection, selectLanguage, reset, dismissError } = useSelection();
  return <section id="language-selection" tabIndex={-1} className="global-selection" aria-labelledby="global-selection-title">
    <div><h2 id="global-selection-title">Explore a language</h2>
      <p>Language applies across all four acts. Ward selection affects census context only.</p></div>
    {census.status === 'ready' ? <label htmlFor="global-language">Selected language
      <select id="global-language" value={selection.language_id} onChange={event => selectLanguage(event.target.value)}>
        <option value="all">All tracked languages</option>
        {census.data.languages.languages.map(language => <option key={language.language_id} value={language.language_id}>{language.display_name}</option>)}
      </select>
    </label> : census.status === 'loading' ? <EmptyState kind="loading" />
      : <EmptyState kind="unavailable" onRetry={reload}>{census.message}</EmptyState>}
    <button type="button" onClick={reset}>Reset selection</button>
    {selection.error ? <EmptyState kind="unavailable" title="Selection corrected" onRetry={dismissError} retryLabel="Dismiss notice">{selection.error}</EmptyState> : null}
  </section>;
}
