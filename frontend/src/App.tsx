import { useEffect, useState } from 'react';
import WardExplorer from './features/map/WardExplorer';
import SpeechLab from './features/speech-lab/SpeechLab';
import Recommendations from './features/recommendations/Recommendations';
import LanguageSelector from './components/LanguageSelector';
import Recovery from './features/recovery/Recovery';
import { SelectionProvider } from './state/selection';
import { ResearchProvider } from './data/ResearchData';

type Connection = 'checking' | 'connected' | 'unavailable';
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const modules = [
  { id: 'discover', act: 'Discover', title: 'Invisible City', description: 'Explore where task-oriented language evaluation is missing, with verified census context.' },
  { id: 'investigate', act: 'Investigate', title: 'Hear What AI Hears', description: 'Compare authentic recordings and measured transcription outcomes, with their limitations.' },
  { id: 'demonstrate', act: 'Demonstrate', title: 'A Second Chance', description: 'Explore a confirmation-first interaction, with one retry and a human-assistance referral option.' },
  { id: 'recommend', act: 'Recommend', title: 'Where Should We Test Next?', description: 'Identify priorities for future evaluation and recruitment from verified evidence.' },
];

export default function App() {
  return <SelectionProvider><ResearchProvider><AppContent /></ResearchProvider></SelectionProvider>;
}

function AppContent() {
  const [connection, setConnection] = useState<Connection>('checking');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setConnection('checking');
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
        if (!response.ok) throw new Error('Health request failed');
        const data: unknown = await response.json();
        if (typeof data !== 'object' || data === null || !('status' in data) || !('mode' in data)
          || data.status !== 'ok' || data.mode !== 'local') throw new Error('Unexpected health response');
        if (active) setConnection('connected');
      } catch {
        if (active) setConnection('unavailable');
      } finally {
        window.clearTimeout(timeout);
      }
    }
    void checkHealth();
    return () => { active = false; window.clearTimeout(timeout); controller.abort(); };
  }, [attempt]);

  return (
    <div className="min-h-screen">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="border-b border-stone-300">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-6">
          <a href="#main" className="brand" aria-label="UNHEARD home">UNHEARD<span aria-hidden="true">.</span></a>
          <span className="text-sm text-stone-600">Sheridan Datathon 2026 · Local research prototype</span>
        </div>
      </header>
      <main id="main" className="mx-auto max-w-6xl px-6 pb-16" tabIndex={-1}>
        <section className="grid gap-8 py-12 md:grid-cols-[1.5fr_1fr] md:py-20" aria-labelledby="intro">
          <div>
            <p className="eyebrow">Every language deserves to be heard</p>
            <h1 id="intro" className="mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">Better questions.<br /><span className="text-emerald-800">More inclusive voices.</span></h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-stone-600">An evidence-based investigation into voice accessibility. Discover the gaps, examine the evidence, and ask where we should test next.</p>
          </div>
          <aside className="status-panel self-center" aria-labelledby="workspace-status">
            <p className="eyebrow" id="workspace-status">Local workspace</p>
            <div role="status" aria-live="polite" className="mt-4">
              <p className="font-semibold">{connection === 'checking' ? 'Checking backend…' : connection === 'connected' ? 'Backend connected' : 'Backend unavailable'}</p>
              <p className="mt-2 text-sm leading-relaxed text-stone-600">{connection === 'unavailable' ? `Start FastAPI at ${API_BASE_URL}, check the URL and CORS settings, then retry. The static ward census explorer remains available.` : connection === 'connected' ? 'The local health service is responding. Census exploration loads independently from verified static assets.' : 'Contacting the local health service. No speech API requests are made.'}</p>
            </div>
            <button className="mt-4 rounded-lg border border-emerald-900 px-4 py-2 text-sm font-semibold disabled:opacity-50" disabled={connection === 'checking'} onClick={() => setAttempt(value => value + 1)}>Retry connection</button>
          </aside>
        </section>
        <LanguageSelector />
        <nav aria-label="Research journey" className="mb-8 flex flex-wrap gap-3">
          {modules.map((module, index) => <a className="journey-link" key={module.id} href={`#${module.id}`}><span className="mr-2 text-stone-500">0{index + 1}</span>{' '}{module.act}</a>)}
        </nav>
        <div className="grid gap-5 md:grid-cols-2">
          {modules.map((module, index) => <section key={module.id} id={module.id} className="module-card scroll-mt-6 min-w-0 md:col-span-2" aria-labelledby={`${module.id}-title`}>
            <div className="flex items-center justify-between gap-4"><p className="eyebrow">0{index + 1} / {module.act}</p><span className="rounded-full bg-stone-100 px-3 py-1 text-xs text-stone-600">{module.id === 'discover' ? '2021 census' : module.id === 'investigate' ? 'Saved evidence' : module.id === 'recommend' ? 'Evaluation priorities' : 'Simulation'}</span></div>
            <h2 id={`${module.id}-title`} className="mt-6 text-2xl font-semibold tracking-tight">{module.title}</h2>
            <p className="mt-3 leading-relaxed text-stone-600">{module.description}</p>
            {module.id === 'discover' ? <WardExplorer /> : null}
            {module.id === 'investigate' ? <SpeechLab /> : null}
            {module.id === 'recommend' ? <Recommendations /> : null}
            {module.id === 'demonstrate' ? <Recovery /> : null}
          </section>)}
        </div>
      </main>
      <footer className="border-t border-stone-300 px-6 py-7 text-center text-sm text-stone-600">Research prototype · No municipal service connection · No live microphone capture</footer>
    </div>
  );
}
