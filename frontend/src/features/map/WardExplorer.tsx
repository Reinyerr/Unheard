import { useEffect, useMemo, useState } from 'react';
import WardTooltip from '../../components/WardTooltip';
import { loadWardGeometry, type WardGeometryResult } from '../../data/wardGeometry';
import { useResearch } from '../../data/ResearchData';
import { useSelection } from '../../state/selection';
import EmptyState from '../../components/EmptyState';
import { colors, coverageLabel, formatCount, formatShare, languageContext, maximum, wardRow } from './metrics';
import WardMap from './WardMap';
import './map.css';

export default function WardExplorer() {
  const { census, reload } = useResearch();
  const data = census.status === 'ready' ? census.data : null;
  const { selection, selectWard, setMetric } = useSelection();
  const languageId = selection.language_id;
  const metric = selection.map_metric;
  const selectedWard = selection.ward_id;
  const [geometry, setGeometry] = useState<WardGeometryResult | null>(null);

  useEffect(() => {
    if (!data) { setGeometry(null); return; }
    const wards = data.wards;
    const controller = new AbortController();
    let active = true;
    setGeometry(null);
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    async function load() {
      try {
        const boundaries = await loadWardGeometry(wards, controller.signal);
        if (active) setGeometry(boundaries);
      } catch {
        if (active) setGeometry({ status: 'unavailable', geometry: null, message: 'Verified boundaries are unavailable. Use the ward table below.' });
      } finally { window.clearTimeout(timeout); }
    }
    void load();
    return () => { active = false; window.clearTimeout(timeout); controller.abort(); };
  }, [data]);

  const language = data?.languages.languages.find(row => row.language_id === languageId);
  const context = languageContext(language);
  const coverage = coverageLabel(language);
  const rows = useMemo(() => data ? data.wards.wards.map(ward => wardRow(ward, languageId)).sort((a, b) => a.ward_id - b.ward_id) : [], [data, languageId]);
  if (census.status === 'unavailable') return <EmptyState kind="unavailable" onRetry={reload}>{census.message} No demographic values are displayed.</EmptyState>;
  if (!data) return <EmptyState kind="loading">Loading corrected census and coverage data.</EmptyState>;
  const missing = data.languages.languages.filter(row => data.wards.missing_request_language_ids.includes(row.language_id));
  const selected = rows.find(row => row.ward_id === selectedWard);
  const max = maximum(rows, metric);
  const cityCounts = missing.map(row => row.city_home_speakers);
  const gapCount = cityCounts.every((value): value is number => value !== null)
    ? cityCounts.reduce((sum, count) => sum + count, 0) : null;
  const tracked = data.languages.languages.filter(row => row.census_home_column !== null);
  const trackedCounts = tracked.map(row => row.city_home_speakers);
  const trackedCount = trackedCounts.every((value): value is number => value !== null)
    ? trackedCounts.reduce((sum, count) => sum + count, 0) : null;
  const gapShare = gapCount !== null && trackedCount !== null && trackedCount > 0 && gapCount <= trackedCount
    ? gapCount / trackedCount : null;
  const cityTotal = languageId === 'all' ? gapCount : language?.city_home_speakers ?? null;

  return <div className="ward-explorer">
    <div className="map-toolbar">
      <div className="ward-controls">
        <fieldset><legend>Map metric</legend><div className="ward-metric-buttons">
          {(['count', 'share'] as const).map(value => <button key={value} type="button" aria-pressed={metric === value}
            onClick={() => setMetric(value)}>{value === 'count' ? 'Speaker count' : 'Share of language base'}</button>)}
        </div></fieldset>
      </div>
      <details className="ward-context">
        <summary>{languageId === 'all' ? `Coverage gap layer · ${missing.length} categories` : `${language?.display_name} · ${language?.coverage_status === 'has_task_audio' ? 'Supplied audio present' : 'Supplied audio gap'}`}</summary>
        <p>{formatCount(cityTotal)} city home-language speakers. {coverage}</p>
        {languageId === 'all' ? <p>{missing.map(row => row.display_name).join(', ')}.</p> : null}
        {language?.census_home_column === null ? <p>This source has no English home-language counts; English is excluded from the tracked non-official census subtotal.</p> : null}
      </details>
    </div>
    <div className="ward-layout">
      <div>
        {geometry?.status === 'ready'
          ? <WardMap geometry={geometry.geometry} rows={rows} metric={metric} selectedWard={selectedWard}
              onSelect={selectWard} context={context} coverage={coverage}
              onUnavailable={() => setGeometry({ status: 'unavailable', geometry: null, message: 'Map rendering is unavailable. Use the verified ward table below.' })} />
          : <div className="ward-map-fallback" role="status">{geometry?.status === 'unavailable' ? geometry.message : 'Loading verified ward boundaries. The census table below is available independently.'}</div>}
        <div className="ward-legend" aria-label={`Color scale: ${metric === 'count' ? 'home-speaker count' : 'share of population language base'}`}>
          {max === null ? <p>No available values for this selection. Gray indicates unavailable data.</p> : <>
            <div className="ward-legend-ramp" aria-hidden="true">{colors.map(color => <span key={color} style={{ backgroundColor: color }} />)}</div>
            <p>0 to {metric === 'count' ? formatCount(max) : formatShare(max)} {metric === 'count' ? 'home speakers' : 'of language base'} · gray = unavailable</p>
          </>}
        </div>
      </div>
      {selected ? <aside key={selectedWard ?? 'no-ward'} className={`ward-detail ${selected ? 'ward-detail-selected' : ''}`} aria-label="Selected ward demographics" aria-live="polite">
        <WardTooltip row={selected} context={context} coverage={coverage} />
          <button className="ward-clear" onClick={() => selectWard(null)}>Clear ward selection</button>
        <p className="ward-detail-note">Census context only. Speech recordings are non-local.</p>
      </aside> : null}
    </div>
    <figure className="coverage-figure" aria-label="Supplied task-audio coverage gap">
      <figcaption>
        <strong>{gapShare === null ? 'Unavailable' : `${(100 * gapShare).toFixed(1)}%`}</strong>
        <div><h2>Home speakers in categories without supplied task audio</h2>
          <p>{formatCount(gapCount)} of {formatCount(trackedCount)} across {tracked.length} tracked non-official categories</p></div>
      </figcaption>
      {gapShare !== null ? <div className="coverage-bar" aria-hidden="true"><span style={{ width: `${gapShare * 100}%` }} /></div> : null}
      <p>MInDS-14 and Speech-MASSIVE subsets · Dataset coverage only</p>
    </figure>
    <details className="ward-table-details" open={geometry?.status === 'unavailable'}>
    <summary>Verified ward table · all 11 wards</summary>
    <div className="ward-table-wrap" tabIndex={0} role="region" aria-label="Scrollable verified ward census table">
      <table className="ward-table">
        <caption>{geometry?.status === 'unavailable' ? 'Verified ward table — map unavailable' : 'Verified ward counts and shares'}: {context}</caption>
        <thead><tr><th scope="col">Ward</th><th scope="col">Home speakers</th><th scope="col">Share</th><th scope="col">Language base</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.ward_id} className={selectedWard === row.ward_id ? 'ward-row-selected' : undefined}>
          <th scope="row"><button aria-pressed={selectedWard === row.ward_id} onClick={() => selectWard(row.ward_id)}>Ward {row.ward_id}</button></th>
          <td>{formatCount(row.count)}</td><td>{formatShare(row.share)}</td><td>{formatCount(row.base)}</td>
        </tr>)}</tbody>
      </table>
    </div>
    <p className="ward-method">Ward share uses the census language base. Missing counts or nonpositive bases have no percentage. The map uses five equal intervals for the active layer.</p>
    </details>
    <details className="ward-provenance"><summary>Sources and boundary limitations</summary>
      <p>City of Mississauga corrected 2021 census and supplied MInDS-14 and Speech-MASSIVE coverage. Home language does not establish English proficiency or recognition performance. The citywide coverage denominator includes only the tracked categories.</p>
      <p>SDG 10 describes the project's focus on inclusion. It does not imply UN endorsement or measured progress.</p>
      <p>Boundaries: <a href="https://data.mississauga.ca/datasets/mississauga::ward-boundaries/about" target="_blank" rel="noreferrer">City of Mississauga Ward Boundaries</a>. No basemap tiles or speech-location markers are loaded.</p>
      {geometry?.status === 'ready' ? <ul>{geometry.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul> : <p>Geometry is not displayed until the T-006 validation/status/hash checks pass.</p>}
    </details>
  </div>;
}
