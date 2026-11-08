import { useEffect, useRef, useState } from 'react';
import WardExplorer from './features/map/WardExplorer';
import SpeechLab from './features/speech-lab/SpeechLab';
import Recommendations from './features/recommendations/Recommendations';
import LanguageSelector from './components/LanguageSelector';
import Recovery from './features/recovery/Recovery';
import AccessibilityNotice from './components/AccessibilityNotice';
import { SelectionProvider } from './state/selection';
import { ResearchProvider } from './data/ResearchData';
import sdg10 from './assets/sdg10-reduced-inequalities.png';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const modules = [
  { id: 'discover', act: 'Discover', title: 'Invisible City', question: 'Which language communities lack supplied task-request evaluation audio?', description: 'Explore missing evaluation coverage alongside verified census context.', limit: 'Home language does not establish English proficiency or recognition performance. Ward shares use the census language base.' },
  { id: 'investigate', act: 'Investigate', title: 'Hear What AI Hears', question: 'How do automatic and guided transcription compare on the same recording?', description: 'Compare authentic recordings and measured transcription outcomes.', limit: 'Eight selected clips per pilot language; scored results may be incomplete. FLEURS speakers have no identified Mississauga ward residency.' },
  { id: 'demonstrate', act: 'Demonstrate', title: 'A Second Chance', question: 'What happens when a user reviews the transcript before accepting it?', description: 'Explore confirmation, one retry and a human-assistance referral option.', limit: 'Judge confirmation is simulated. Referral contacts nobody. Unavailable or unapproved voice prompts remain text-only.' },
  { id: 'recommend', act: 'Recommend', title: 'Where Should We Test Next?', question: 'Where could future language evaluation and recruitment focus?', description: 'Identify priorities from coverage gaps and verified census context.', limit: 'Coverage and population determine priorities. Pilot error rates remain separate; there is no ward-level failure forecast.' },
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
      else if (!window.location.hash) setStep(0);
    };
    window.addEventListener('hashchange', followHash);
    return () => window.removeEventListener('hashchange', followHash);
  }, []);
  useEffect(() => {
    // Retain local sessions and selections, but pause audio in inactive acts.
    stage.current?.querySelectorAll<HTMLMediaElement>('section[hidden] audio').forEach(audio => audio.pause());
    if (previousStep.current === step) return;
    previousStep.current = step;
    if (stage.current) stage.current.scrollTop = 0;
    document.getElementById(modules[step].id)?.querySelector<HTMLElement>('h1, h2')?.focus({ preventScroll: true });
  }, [step]);
  function go(index: number) {
    setStep(index);
    if (window.location.hash !== `#${modules[index].id}`) window.location.hash = modules[index].id;
  }

  return (
    <div className="demo-shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header">
        <a href="#discover" className="brand" aria-label="UNHEARD home">UNHEARD<span aria-hidden="true">.</span></a>
        <span className="prototype-label"><span aria-hidden="true" /> Language access research / Mississauga</span>
        <span className="sdg-label">Aligned with SDG 10</span>
      </header>
      <div className="journey-topbar">
        <nav aria-label="Research journey" className="journey-navigation">
          {modules.map((module, index) => <button type="button" key={module.id} onClick={() => go(index)}
            aria-current={step === index ? 'step' : undefined} className={index < step ? 'step-complete' : ''}>
            <span className="step-number">{String(index + 1).padStart(2, '0')}</span>{' '}<span>{module.act}</span>
          </button>)}
        </nav>
        <p className="journey-count" aria-live="polite">Step {step + 1} of 4</p>
      </div>
      <LanguageSelector />
      <main id="main" tabIndex={-1} className="journey-main">
        <div ref={stage} className="journey-stage">
          {modules.map((module, index) => <section key={module.id} id={module.id} hidden={step !== index}
            className={`journey-act ${module.id === 'discover' ? 'discover-act' : ''}`} aria-labelledby={`${module.id}-title`}>
            <div className="act-heading"><div><p className="eyebrow">0{index + 1} / {module.act}</p>
              {module.id === 'discover' ? <><h1 id="discover-title" tabIndex={-1}>Language coverage by ward</h1>

                </>
                : <><h2 id={`${module.id}-title`} tabIndex={-1}>{module.title}</h2><p className="act-question">{module.question}</p></>}
              </div>
              {module.id === 'discover' ? <a className="sdg-artwork" href="https://sdgs.un.org/goals/goal10" target="_blank" rel="noreferrer">
                <img src={sdg10} alt="UN Sustainable Development Goal 10: Reduced Inequalities." width="132" height="132" />
                <span>SDG 10 · Reduced inequalities</span></a>
                : <span className="evidence-tag">{module.id === 'investigate' ? 'Saved evidence' : module.id === 'demonstrate' ? 'Interaction simulation' : 'Future evaluation'}</span>}
            </div>
            <p className="act-limit">{module.limit}</p>
            {module.id === 'discover' ? <>
              <WardExplorer /><AccessibilityNotice />
            </> : null}
            {module.id === 'investigate' ? <SpeechLab /> : null}
            {module.id === 'demonstrate' ? <Recovery active={step === index} /> : null}
            {module.id === 'recommend' ? <><div className="sdg-closing">
              <img src={sdg10} alt="UN Sustainable Development Goal 10: Reduced Inequalities." width="80" height="80" />
              <div><strong>SDG 10 · Reduced inequalities</strong><p>Priorities for future language evaluation and recruitment.</p>
                <p className="speech-note">Aligned with SDG 10. No UN endorsement or proven reduction in inequality is claimed.</p></div>
              </div><Recommendations /></> : null}
          </section>)}
        </div>
      </main>
      <nav className="journey-footer" aria-label="Step navigation">
        <button type="button" className="back-button" disabled={step === 0} onClick={() => go(step - 1)}>← Back</button>

        <button type="button" className="primary-button" onClick={() => go(step === 3 ? 0 : step + 1)}>
          {step === 3 ? 'Return to Discover' : `Next: ${modules[step + 1].act}`} <span aria-hidden="true">→</span>
        </button>
      </nav>
    </div>
  );
}
