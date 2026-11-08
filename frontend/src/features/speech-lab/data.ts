import { useEffect, useState } from 'react';
import { validateArtifact, type Samples, type Experiments } from '../../types/research';
import type { Resource } from '../../data/ResearchData';

export function useSamples() {
  const [resource, setResource] = useState<Resource<Samples>>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setResource({ status: 'loading' });
    void (async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}data/samples.v1.json`, { signal: controller.signal });
        if (!response.ok) throw new Error('Missing sample manifest');
        const data = validateArtifact('samples', await response.json());
        if (active) setResource({ status: 'ready', data });
      } catch { if (active) setResource({ status: 'unavailable', message: 'The vetted sample manifest is unavailable or invalid. No replacement audio is used.' }); }
      finally { window.clearTimeout(timeout); }
    })();
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [attempt]);
  return { resource, reload: () => setAttempt(value => value + 1) };
}
export function matchingEvidence(samples: Samples, experiments: Experiments): boolean {
  const digest = samples.source.selection_sha256;
  return Boolean(digest && digest === experiments.source.selection_sha256)
    && experiments.records.every(record => samples.samples.some(sample => sample.sample_id === record.sample_id
      && sample.language_id === record.language_id && sample.fleurs_id === record.fleurs_id));
}
export const percent = (value: number | null) => value === null ? 'Not available' : `${(value * 100).toFixed(1)}%`;
export const delta = (value: number | null) => value === null ? 'Not available' : `${value > 0 ? '+' : ''}${(value * 100).toFixed(1)} percentage points`;
