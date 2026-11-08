import type { Languages, LanguageId, MapMetric, Recommendations, Wards } from '../../types/research';
import { metricValue, wardRow, type WardMetricRow } from '../map/metrics';

export function rankedWards(wards: Wards, language: LanguageId, metric: MapMetric): WardMetricRow[] {
  return wards.wards.map(ward => wardRow(ward, language)).filter(row => metricValue(row, metric) !== null)
    .sort((a, b) => (metricValue(b, metric) ?? 0) - (metricValue(a, metric) ?? 0) || a.ward_id - b.ward_id);
}
/** Fail closed on stale/mismatched ranking exports; speech evidence is never an input. */
export function rankingError(data: Recommendations, languages: Languages, wards: Wards): string | null {
  const expected = languages.languages.filter(row => row.coverage_status === 'no_task_audio')
    .sort((a, b) => (b.city_home_speakers ?? -1) - (a.city_home_speakers ?? -1) || a.language_id.localeCompare(b.language_id));
  const rows = [...data.items].sort((a, b) => a.rank - b.rank);
  const sourceKey = `${wards.source_file}:sha256`;
  if (!wards.source[sourceKey] || data.source[sourceKey] !== wards.source[sourceKey]) return 'Recommendation and corrected census provenance do not match.';
  if (rows.length !== expected.length || rows.some((row, i) => row.rank !== i + 1
    || row.language_id !== expected[i].language_id || row.city_home_speakers !== expected[i].city_home_speakers)) return 'Recommendation ranks do not agree with supplied coverage and home-language counts.';
  for (const row of rows) {
    const top = rankedWards(wards, row.language_id, 'count').slice(0, 3).map(ward => ward.ward_id);
    if (row.suggested_ward_ids.length !== top.length || top.some((id, i) => row.suggested_ward_ids[i] !== id)) return 'Suggested ward IDs do not agree with the exported count-ranking policy.';
  }
  return null;
}
