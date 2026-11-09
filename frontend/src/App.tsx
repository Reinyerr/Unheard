import { useEffect, useRef, useState } from 'react';
import WardExplorer from './features/map/WardExplorer';
import SpeechLab from './features/speech-lab/SpeechLab';
import LanguageSelector from './components/LanguageSelector';
import Recovery from './features/recovery/Recovery';
import AccessibilityNotice from './components/AccessibilityNotice';
import { SelectionProvider } from './state/selection';
import { ResearchProvider } from './data/ResearchData';
import sdg10 from './assets/sdg10-reduced-inequalities.png';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const modules = [
  { id: 'discover', act: 'Discover', title: 'Language coverage by ward' },
  { id: 'investigate', act: 'Investigate', title: 'Hear What AI Hears' },
  { id: 'demonstrate', act: 'Demonstrate', title: 'A Second Chance' },
];

export default function App() {
  return <SelectionProvider><ResearchProvider><AppContent /></ResearchProvider></SelectionProvider>;
}

export function AppContent() {
  const stepFromHash = () => Math.max(0, modules.findIndex(module => `#${module.id}` === window.location.hash));
  const [step, setStep] = useState(stepFromHash);
  const stage = useRef<HTMLDivElement>(null);
  const previousStep = useRef(step);

  useEffect(() => {
    const followHash = () => {
      const index = modules.findIndex(module => `#${module.id}` === window.location.hash);
      if (index >= 0) setStep(index);
      else if (!window.location.hash || window.location.hash === '#recommend') setStep(0);
    };
    window.addEventListener('hashchange', followHash);
    return () => window.removeEventListener('hashchange', followHash);
  }, []);
  useEffect(() => {
    // Retain local sessions and selections, but pause audio in inactive acts.
    stage.current?.querySelectorAll<HTMLMediaElement>('section[hidden] audio').forEach(audio => audio.pause());
    if (previousStep.current === step) return;
    previousStep.current = step;
    window.scrollTo(0, 0);
    document.getElementById(modules[step].id)?.querySelector<HTMLElement>('h1, h2')?.focus({ preventScroll: true });
  }, [step]);
  function go(index: number) {
    setStep(index);
    if (window.location.hash !== `#${modules[index].id}`) window.history.pushState(null, '', `#${modules[index].id}`);
  }

  const lastStep = step === modules.length - 1;
  return (
    <div className="demo-shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header">
        <a href="#discover" className="brand" aria-label="UNHEARD home">UNHEARD<span aria-hidden="true">.</span></a>
        <nav aria-label="Research journey" className="journey-navigation">
          {modules.map((module, index) => <button type="button" key={module.id} onClick={() => go(index)}
            aria-current={step === index ? 'step' : undefined}>
            <span className="step-number">{String(index + 1).padStart(2, '0')}</span>{' '}<span>{module.act}</span>
          </button>)}
        </nav>
      </header>
      <LanguageSelector />
      <main id="main" tabIndex={-1} className="journey-main">
        <div ref={stage} className="journey-stage">
          {modules.map((module, index) => <section key={module.id} id={module.id} hidden={step !== index}
            className="journey-act" aria-labelledby={`${module.id}-title`}>
            <div className="act-heading">
              {module.id === 'discover' ? <h1 id="discover-title" tabIndex={-1}>{module.title}</h1>
                : <h2 id={`${module.id}-title`} tabIndex={-1}>{module.title}</h2>}
              {module.id === 'discover' ? <a className="sdg-artwork" href="https://sdgs.un.org/goals/goal10" target="_blank" rel="noreferrer">
                <img src={sdg10} alt="UN Sustainable Development Goal 10: Reduced Inequalities." width="132" height="132" />
                <span>Aligned with SDG 10</span></a> : null}
            </div>
            {module.id === 'discover' ? <>
              <WardExplorer /><AccessibilityNotice />
            </> : null}
            {module.id === 'investigate' ? <SpeechLab /> : null}
            {module.id === 'demonstrate' ? <Recovery active={step === index} /> : null}
          </section>)}
        </div>
      </main>
      <nav className="journey-footer" aria-label="Step navigation">
        <button type="button" className="back-button" disabled={step === 0} onClick={() => go(step - 1)}>← Back</button>

        <button type="button" className="primary-button" onClick={() => go(lastStep ? 0 : step + 1)}>
          {lastStep ? 'Return to Discover' : `Next: ${modules[step + 1].act}`}
        </button>
      </nav>
    </div>
  );
}
