import type { Language, LanguageId, MapMetric, Ward } from '../../types/research';

export type MapLanguage = LanguageId | 'all';
export type WardMetricRow = { ward_id: number; count: number | null; share: number | null; base: number | null };
export const colors = ['#edf8f5', '#c7e8df', '#8dcbb7', '#489f85', '#14664f'];
export const unavailableColor = '#d5d8db';
const counts = new Intl.NumberFormat('en-CA');
const shares = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 2 });
export const formatCount = (value: number | null) => value === null ? 'Unavailable' : counts.format(value);
export const formatShare = (value: number | null) => value === null ? 'Unavailable' : `${shares.format(value)}%`;

export function wardRow(ward: Ward, language: MapLanguage): WardMetricRow {
  const count = language === 'all' ? ward.gap_population : ward.home_speakers_by_language[language] ?? null;
  const base = ward.population_language_base;
  return { ward_id: ward.ward_id, count, base,
    share: count !== null && base !== null && base > 0 ? 100 * count / base : null };
}
export const metricValue = (row: WardMetricRow, metric: MapMetric) => metric === 'count' ? row.count : row.share;
export function maximum(rows: WardMetricRow[], metric: MapMetric): number | null {
  const values = rows.map(row => metricValue(row, metric)).filter((value): value is number => value !== null);
  return values.length ? Math.max(...values) : null;
}
export function fillColor(row: WardMetricRow, metric: MapMetric, max: number | null): string {
  const value = metricValue(row, metric);
  if (value === null || max === null) return unavailableColor;
  return colors[max === 0 ? 0 : Math.min(colors.length - 1, Math.floor(value / max * colors.length))];
}
export function languageContext(language: Language | undefined) {
  return language ? `${language.display_name} home-language speakers` : 'Eight supplied categories without task-request audio';
}
export function coverageLabel(language: Language | undefined) {
  return language?.coverage_status === 'has_task_audio' ? 'Covered: task-request audio is present in the supplied subsets.'
    : 'Coverage gap: no task-request audio in the supplied subsets.';
}
