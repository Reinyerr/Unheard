import AudioWaveform from '../../components/AudioWaveform';
import { useEffect, useRef, useState } from 'react';
import { useSelection } from '../../state/selection';
import { useResearch } from '../../data/ResearchData';
import EmptyState, { statusLabels } from '../../components/EmptyState';
import { matchingEvidence, useSamples } from '../speech-lab/data';
import { type Sample } from '../../types/research';
import { capabilitiesSchema, NOTICE, offlineAttempt, REFERRAL, request, sessionSchema, type Capabilities, type Session } from './data';
import PromptAudio from './PromptAudio';
import { recoveryPrompt, TTS_MODEL } from './prompts';
import './recovery.css';

function Recording({ sample }: { sample: Sample }) {
  return <div><AudioWaveform src={`${import.meta.env.BASE_URL}${sample.audio_path}`} label={`Prerecorded FLEURS clip ${sample.sample_id}`} />
    <details><summary>Recording reference transcript · supplied text</summary>
      <p className="speech-transcript" lang={recoveryPrompt(sample.language_id)?.language_code} dir={sample.language_id === 'urdu' || sample.language_id === 'arabic' ? 'rtl' : 'ltr'}>{sample.raw_reference_transcript}</p>
      <p className="speech-note">Dataset reference, separate from the provider transcript you confirm. This text does not establish original-speaker consent.</p>
    </details></div>;
}

export default function Recovery({ active = true }: { active?: boolean }) {
  const { selection } = useSelection();
  // Remount synchronously on language/revision changes: dispose audio, sessions and pending requests.
  return <Flow key={`${selection.language_id}:${selection.language_revision}`} active={active} />;
}

function Flow({ active }: { active: boolean }) {
  const { selection } = useSelection();
  const { census, experiments } = useResearch();
  const { resource } = useSamples();
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [connection, setConnection] = useState('Checking backend…');
  const [route, setRoute] = useState<'backend' | 'offline'>('backend');
  const [mode, setMode] = useState<Session['mode']>('auto');
  const [source, setSource] = useState<'saved' | 'live'>('saved');
  const [sampleId, setSampleId] = useState('');
  const [session, setSession] = useState<Session | null>(null);
  const [busy, setBusy] = useState(false);
  const [pendingMessage, setPendingMessage] = useState('Processing…');
  const [error, setError] = useState('');
  const [uncertain, setUncertain] = useState(false);
  const [check, setCheck] = useState(0);
  const pending = useRef<AbortController | null>(null);
  const outcomePanel = useRef<HTMLDivElement>(null);
  const recordingSelect = useRef<HTMLSelectElement>(null);
  const restarting = useRef(false);
  const alive = useRef(true);
  useEffect(() => {
    if (!active) return;
    if (restarting.current && !session && !uncertain) {
      recordingSelect.current?.focus();
      restarting.current = false;
    } else if (!busy && (session || uncertain || error)) {
      outcomePanel.current?.focus();
    }
  }, [session, uncertain, error, busy]);
  useEffect(() => { alive.current = true; return () => { alive.current = false; pending.current?.abort(); }; }, []);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 7000);
    let active = true;
    setConnection('Checking backend…');
    void request('capabilities', controller.signal).then(value => {
      const parsed = capabilitiesSchema.parse(value);
      if (active) { setCapabilities(parsed.available ? parsed : null); setConnection(parsed.available ? 'Backend available' : 'Backend data unavailable'); }
    }).catch(() => { if (active) { setCapabilities(null); setConnection('Backend unavailable · saved browser route available when evidence exists'); } })
      .finally(() => window.clearTimeout(timeout));
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [check]);
  const samples = resource.status === 'ready' ? resource.data : null;
  const evidence = samples && experiments.status === 'ready' && matchingEvidence(samples, experiments.data) ? experiments.data : null;
  const choices = samples?.samples.filter(row => row.language_id === selection.language_id) ?? [];
  const language = census.status === 'ready' ? census.data.languages.languages.find(row => row.language_id === selection.language_id) : undefined;
  const capability = capabilities?.languages.find(row => row.language_id === selection.language_id);
  const sample = choices.find(row => row.sample_id === (session?.sample_id ?? sampleId));
  const retryIds = session?.retry_sample_ids ?? [];
  const prompt = recoveryPrompt(selection.language_id);
  const eligible = session ? choices.filter(row => retryIds.includes(row.sample_id)) : choices;

  async function send(path: string, body: object) {
    if (busy || uncertain) return;
    const controller = new AbortController();
    pending.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 45000);
    setPendingMessage(path === 'decision' ? 'Saving your choice…'
      : path === 'retry' ? 'Checking the next recording…'
        : source === 'live' ? 'Transcribing the recording…' : 'Preparing the saved transcript…');
    setBusy(true); setError('');
    try {
      const value = await request(path, controller.signal, body);
      if (!alive.current) return;
      const envelope = typeof value === 'object' && value !== null ? value as Record<string, unknown> : {};
      const candidate = envelope.session ?? (!envelope.error ? value : null);
      if (candidate) {
        const next = sessionSchema.parse(candidate);
        if (next.language_id !== selection.language_id || !choices.some(row => row.sample_id === next.sample_id)
          || (session && next.session_id !== session.session_id)) throw new Error('Mismatched session');
        setSession(next); setSampleId('');
      }
      if (envelope.error) {
        const detail = envelope.error as Record<string, unknown>;
        setError(typeof detail.message === 'string' ? detail.message : 'Request failed; no result is inferred.');
        // Expired/invalid server sessions must still offer a usable way forward.
        if (session && !candidate) setUncertain(true);
      }
      if (!candidate && !envelope.error) throw new Error('Invalid response');
    } catch {
      if (alive.current) { setError('Backend response unavailable. The request may have completed; do not replay it automatically. Start a separate saved browser simulation or check the backend.'); setUncertain(true); }
    } finally { window.clearTimeout(timeout); if (alive.current) setBusy(false); }
  }

  function attempt() {
    if (!sampleId || !samples || !language) return;
    if (route === 'offline') {
      if (!evidence || session && (!session.retry_available || !retryIds.includes(sampleId))) return;
      setSession(offlineAttempt(session, sampleId, language.language_id, mode, samples, evidence));
      setSampleId(''); setError('');
    } else if (session) void send('retry', { session_id: session.session_id, sample_id: sampleId });
    else void send('start', { language_id: language.language_id, sample_id: sampleId, source, mode, allow_saved_fallback: true });
  }
  function decide(decision: 'correct' | 'incorrect' | 'refer') {
    if (!session || busy || uncertain) return;
    if (route === 'backend') { void send('decision', { session_id: session.session_id, decision }); return; }
    if (decision !== 'refer' && session.state !== 'confirm') return;
    if (decision === 'refer' && !['confirm', 'retry_or_refer'].includes(session.state)) return;
    const state = decision === 'correct' ? 'accepted' : decision === 'refer' || session.attempts >= 2 ? 'referral' : 'retry_or_refer';
    setSession({ ...session, state, retry_available: state === 'retry_or_refer' && session.attempts < 2 && retryIds.length > 0,
      referral_message: state === 'referral' || state === 'retry_or_refer' ? REFERRAL : null });
  }

  function restart() {
    restarting.current = true;
    setSession(null); setSampleId(''); setError(''); setUncertain(false);
    setRoute('offline'); setSource('saved');
  }

  const finished = session?.state === 'accepted' || session?.state === 'referral';
  const feedback = busy ? { title: pendingMessage, message: '', tone: 'pending' }
    : uncertain ? { title: 'We couldn’t confirm the result.', message: 'The backend request may have completed. Don’t repeat it automatically. You can start a separate saved browser simulation below.', tone: 'warning' }
      : session?.state === 'accepted' ? { title: 'Transcript accepted.', message: 'You confirmed the text in this simulation. No service request was sent.', tone: 'success' }
        : session?.state === 'referral' ? { title: 'Consider human assistance.', message: '', tone: 'warning' }
          : session?.state === 'retry_or_refer' ? {
            title: session.retry_available ? 'Let’s try once more.' : 'No retry is available.',
            message: session.retry_available
              ? `${session.transcript ? 'You marked the transcript incorrect.' : 'No usable transcript was available.'} Choose a different recording below for your one remaining attempt, or choose human assistance.`
              : 'Choose the human-assistance referral option to finish this simulation.', tone: 'warning' }
            : session?.state === 'confirm' ? { title: 'Review what the AI heard.', message: session.attempts >= session.max_attempts ? 'This is the final attempt.' : 'One retry is available.', tone: 'review' }
              : error ? { title: 'The simulation could not start.', message: 'Review the error below. You can choose another recording or the browser-only saved route.', tone: 'warning' }
                : { title: 'Choose a recording to begin.', message: '', tone: 'ready' };

  if (selection.language_id === 'all') return <EmptyState kind="choose_language">Select a pilot language above to start a simulated confirmation.</EmptyState>;
  if (census.status === 'loading' || resource.status === 'loading') return <EmptyState kind="loading" />;
  if (census.status !== 'ready' || !samples) return <EmptyState kind="unavailable">Verified language/sample assets are unavailable.</EmptyState>;
  if (!language?.pilot_selected) return <EmptyState kind="not_tested">This language is outside the prerecorded pilot. No voice support or result is inferred.</EmptyState>;
  const disabled = busy || uncertain;
  return <div className="recovery">
    <p className="recovery-context">{language.display_name} · {choices.length} recordings · {connection}</p>
    <details className="simulation-disclosure"><summary>Judge-controlled interaction simulation</summary><p>{NOTICE}</p></details>
    {!session ? <div className="recovery-settings">
      <label>Demo route<select disabled={busy} value={route} onChange={event => { setRoute(event.target.value as typeof route); setSource('saved'); setUncertain(false); setError(''); }}>
        <option value="backend">Local backend</option><option value="offline">Browser-only saved results</option>
      </select></label>
      <label>Transcription setting<select disabled={busy} value={mode} onChange={event => { setMode(event.target.value as typeof mode); setSource('saved'); }}><option value="auto">Automatic detection</option><option value="guided">Guided language</option></select></label>
      {route === 'backend' ? <label>Result origin<select disabled={busy} value={source} onChange={event => setSource(event.target.value as typeof source)}><option value="saved">Saved actual provider response</option><option value="live" disabled={!capabilities?.live_configured || mode === 'guided' && !capability?.guided_verified}>Live provider request (may incur charges)</option></select></label> : null}
      {source === 'live' ? <p>One live request per attempt, with same-mode saved fallback if available. Key presence does not verify credits or connectivity.</p> : null}
    </div> : null}
    <div ref={outcomePanel} tabIndex={-1} className={`recovery-outcome recovery-outcome-${feedback.tone}`} role="status" aria-live="polite" aria-atomic="true">
      <h3>{feedback.title}</h3>{feedback.message ? <p>{feedback.message}</p> : null}
      <p className="recovery-progress"><strong>State: {busy ? 'Processing request…' : session?.state.replaceAll('_', ' ') ?? 'ready'}</strong>{session ? ` · attempt ${session.attempts} of ${session.max_attempts}` : ''}</p>
    </div>
    {finished || uncertain ? <div className="recovery-next">
      <button disabled={busy} onClick={restart}>Start separate saved browser simulation</button>
      {finished && !busy && !uncertain ? <a className="recovery-continue" href="#discover">Return to ward map</a> : null}
    </div> : null}
    {session ? <div className="recovery-result-details">
      <p>Result: {statusLabels[session.transcription_status]} · origin: {session.source ?? 'no outcome'} · {session.mode}. {session.fallback_reason ? `Fallback: ${session.fallback_reason}.` : ''}</p>
      {session?.referral_message ? <p>{session.referral_message}</p> : null}
    </div> : null}
    {error ? <p role="alert">{error}</p> : null}
    {route === 'offline' && !evidence ? <EmptyState kind="unavailable">Matching saved experiment evidence is unavailable. No transcript can be substituted.</EmptyState> : null}
    {!session || session.retry_available ? <>
      <label>{session ? 'Different recording for the single simulated retry' : 'Prerecorded sample'}<select ref={recordingSelect} value={sampleId} disabled={disabled} onChange={event => setSampleId(event.target.value)}>
        <option value="">Choose a recording</option>{eligible.map(row => {
          const outcome = evidence?.records.find(record => record.sample_id === row.sample_id)?.[mode];
          return <option value={row.sample_id} key={row.sample_id}>{row.sample_id} · {route === 'backend' && capability?.saved_sample_ids_by_mode[mode].includes(row.sample_id) ? 'usable saved result' : outcome ? statusLabels[outcome.status] : 'saved result unavailable'}</option>;
        })}
      </select></label>
      <button disabled={disabled || !sampleId || route === 'offline' && !evidence || route === 'backend' && !capability} onClick={attempt}>{busy ? 'Processing…' : session ? 'Try Different Sample' : source === 'live' ? 'Start live transcription (uses credits)' : 'Start saved simulation'}</button>
    </> : null}
    {sample ? <section key={sample.sample_id} aria-label="Current demo recording"><h3>{sample.sample_id} · FLEURS ID {sample.fleurs_id}</h3><Recording sample={sample} />
      {session?.transcript ? <><h3>Actual {session.source} transcript</h3><p className="speech-transcript" dir={language.language_id === 'urdu' || language.language_id === 'arabic' ? 'rtl' : 'ltr'} lang={language.dataset_language_code}>{session.transcript}</p></> : null}
    </section> : null}
    {session?.state === 'confirm' ? <>{!busy ? <PromptAudio key={`${session.session_id}:${session.sample_id}`} language={language.language_id} /> : null}
      <p><strong>Is this transcript correct?</strong> Your choice applies only to this simulation.</p>
      <div className="recovery-actions"><button disabled={disabled} onClick={() => decide('correct')}>{prompt?.correct_label ?? 'Correct'}{language.language_id !== 'english' ? ' (Correct)' : ''}</button><button disabled={disabled} onClick={() => decide('incorrect')}>{prompt?.incorrect_label ?? 'Incorrect'}{language.language_id !== 'english' ? ' (Incorrect)' : ''}</button></div></> : null}
    {session && ['confirm', 'retry_or_refer'].includes(session.state) ? <button disabled={disabled} onClick={() => decide('refer')}>Human-assistance referral option</button> : null}
    {prompt && session?.state !== 'confirm' ? <details><summary>{prompt.display_name} recovery prompt · configured, unverified</summary>
      <p dir={prompt.direction === 'rtl' ? 'rtl' : 'ltr'} lang={prompt.language_code}>{prompt.text}</p>
      <p>Draft authored instruction; language review pending until audio approval. Selected voice: <bdi>{prompt.voice_id}</bdi> · model: {TTS_MODEL}. Configuration alone does not establish account access or voice compatibility.</p></details> : null}
    <button disabled={busy || connection === 'Checking backend…'} onClick={() => setCheck(value => value + 1)}>{connection === 'Checking backend…' ? 'Checking backend…' : 'Refresh backend availability'}</button>
    <details><summary>Recording provenance and limitations</summary><p>{samples.source.attribution} · <a href="https://huggingface.co/datasets/google/fleurs">FLEURS</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p><p>{samples.source.modifications}</p><p>{samples.samples.length} selected clips, seed {samples.selection.seed}. Selection SHA-256: <span className="speech-hash">{samples.source.selection_sha256}</span>.</p><p>FLEURS is non-local read speech. A retry uses a different clip for simulation. Browser sessions use matching saved outputs without review flags and run independently of backend sessions.</p></details>
  </div>;
}
