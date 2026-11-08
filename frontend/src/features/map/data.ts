import { validateArtifact, type Languages, type Wards } from '../../types/research';

export type MapData = { wards: Wards; languages: Languages };

/** Real generated artifacts only; demographic inconsistencies block display. */
export async function loadMapData(signal: AbortSignal): Promise<MapData> {
  const base = import.meta.env.BASE_URL;
  const [wardResponse, languageResponse] = await Promise.all([
    fetch(`${base}data/wards.v1.json`, { signal }), fetch(`${base}data/languages.v1.json`, { signal }),
  ]);
  if (!wardResponse.ok || !languageResponse.ok) throw new Error('Verified census data is unavailable.');
  const wards = validateArtifact('wards', await wardResponse.json());
  const languages = validateArtifact('languages', await languageResponse.json());
  if (wards.wards.length !== 11 || wards.wards.map(row => row.ward_id).sort((a, b) => a - b).some((id, i) => id !== i + 1)) {
    throw new Error('Corrected census must contain all 11 unique wards.');
  }
  const missing = languages.languages.filter(row => row.coverage_status === 'no_task_audio').map(row => row.language_id);
  if (missing.length !== 8 || wards.missing_request_language_ids.length !== 8
    || missing.some(id => !wards.missing_request_language_ids.includes(id))) throw new Error('Coverage and census gap categories disagree.');
  for (const ward of wards.wards) {
    const values = missing.map(id => ward.home_speakers_by_language[id] ?? null);
    const expected = values.every((value): value is number => value !== null) ? values.reduce((a, b) => a + b, 0) : null;
    if (expected !== ward.gap_population) throw new Error('Ward coverage-gap total disagrees with its source categories.');
  }
  for (const language of languages.languages.filter(row => row.census_home_column !== null)) {
    const values = wards.wards.map(ward => ward.home_speakers_by_language[language.language_id] ?? null);
    if (language.city_home_speakers !== null && values.every((value): value is number => value !== null)
      && values.reduce((a, b) => a + b, 0) !== language.city_home_speakers) throw new Error('City and ward language totals disagree.');
  }
  return { wards, languages };
}
