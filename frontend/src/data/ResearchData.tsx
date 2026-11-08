import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { loadMapData, type MapData } from '../features/map/data';
import { validateArtifact, type Experiments, type Recommendations } from '../types/research';

export type Resource<T> = { status: 'loading' } | { status: 'unavailable'; message: string } | { status: 'ready'; data: T };
type ResearchData = { census: Resource<MapData>; experiments: Resource<Experiments>;
  recommendations: Resource<Recommendations>; reload: () => void };
const Context = createContext<ResearchData | null>(null);

/** Each static module can fail independently; no fixtures, backend calls or invented outcomes. */
export function ResearchProvider({ children }: { children: ReactNode }) {
  const [census, setCensus] = useState<Resource<MapData>>({ status: 'loading' });
  const [experiments, setExperiments] = useState<Resource<Experiments>>({ status: 'loading' });
  const [recommendations, setRecommendations] = useState<Resource<Recommendations>>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setCensus({ status: 'loading' }); setExperiments({ status: 'loading' }); setRecommendations({ status: 'loading' });
    const tasks = [
      loadMapData(controller.signal).then(data => { if (active) setCensus({ status: 'ready', data }); })
        .catch(() => { if (active) setCensus({ status: 'unavailable', message: 'Verified census/coverage assets could not be loaded or did not agree.' }); }),
      (async () => {
        try {
          const response = await fetch(`${import.meta.env.BASE_URL}data/experiments.v1.json`, { signal: controller.signal });
          if (!response.ok) throw new Error('Unavailable');
          const data = validateArtifact('experiments', await response.json());
          if (active) setExperiments({ status: 'ready', data });
        } catch { if (active) setExperiments({ status: 'unavailable', message: 'Saved experiment evidence is unavailable. Missing files are not recognition results.' }); }
      })(),
      (async () => {
        try {
          const response = await fetch(`${import.meta.env.BASE_URL}data/recommendations.v1.json`, { signal: controller.signal });
          if (!response.ok) throw new Error('Unavailable');
          const data = validateArtifact('recommendations', await response.json());
          if (active) setRecommendations({ status: 'ready', data });
        } catch { if (active) setRecommendations({ status: 'unavailable', message: 'Verified recommendation data is unavailable.' }); }
      })(),
    ];
    void Promise.allSettled(tasks).then(() => window.clearTimeout(timeout));
    return () => { active = false; window.clearTimeout(timeout); controller.abort(); };
  }, [attempt]);
  return <Context.Provider value={{ census, experiments, recommendations, reload: () => setAttempt(value => value + 1) }}>{children}</Context.Provider>;
}
export function useResearch(): ResearchData {
  const value = useContext(Context);
  if (!value) throw new Error('ResearchProvider is required');
  return value;
}
