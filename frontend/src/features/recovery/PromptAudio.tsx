import { useEffect, useRef, useState } from 'react';
import { z } from 'zod';
import { PROMPT_REVISION, recoveryPrompt, TTS_ATTRIBUTION, TTS_MODEL } from './prompts';

const manifestSchema = z.object({ schema_version: z.literal('2.0'), language_id: z.string(), language_code: z.string(),
  text: z.string(), prompt_revision: z.literal(PROMPT_REVISION), provider: z.literal('elevenlabs'), model_id: z.literal(TTS_MODEL),
  voice_id: z.string(), generated_at_utc: z.string().min(1), origin: z.literal('saved'),
  audio_path: z.string(), audio_sha256: z.string().regex(/^[a-f0-9]{64}$/),
  review_status: z.literal('approved'), human_listened: z.literal(true), language_reviewed: z.literal(true),
  approved_at_utc: z.string().min(1), rights_reviewed: z.literal(true), attribution: z.literal(TTS_ATTRIBUTION),
  verification: z.object({ synthesis_http_status: z.literal(200), model_language_advertised: z.literal(true), voice_access: z.literal('accessible') }) });

function Player({ url, onError }: { url: string; onError: () => void }) {
  const audio = useRef<HTMLAudioElement>(null);
  useEffect(() => { const player = audio.current; return () => player?.pause(); }, []);
  return <audio ref={audio} controls preload="metadata" src={url} aria-label="Cached simulated confirmation instruction" onError={onError} />;
}

export default function PromptAudio({ language }: { language: string }) {
  const config = recoveryPrompt(language);
  const [prompt, setPrompt] = useState<{ url: string; attribution: string; generated: string } | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 10000);
    let active = true;
    let url: string | undefined;
    setPrompt(null); setFailed(false);
    if (config) void (async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}audio/prompts/${language}/manifest.json`, { signal: controller.signal });
        if (!response.ok) return;
        const manifest = manifestSchema.parse(await response.json());
        if (manifest.language_id !== language || manifest.language_code !== config.language_code
          || manifest.voice_id !== config.voice_id || manifest.text !== config.text
          || manifest.audio_path !== `audio/prompts/${language}/confirm.mp3`) return;
        const clip = await fetch(`${import.meta.env.BASE_URL}${manifest.audio_path}`, { signal: controller.signal });
        if (!clip.ok) return;
        const bytes = await clip.arrayBuffer();
        if (bytes.byteLength <= 128 || bytes.byteLength > 2_000_000) return;
        const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), v => v.toString(16).padStart(2, '0')).join('');
        if (hash !== manifest.audio_sha256 || !active) return;
        url = URL.createObjectURL(new Blob([bytes], { type: 'audio/mpeg' }));
        setPrompt({ url, attribution: manifest.attribution, generated: manifest.generated_at_utc });
      } catch { /* No vetted prompt: retain explicit text-only fallback. */ }
      finally { window.clearTimeout(timeout); }
    })();
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); if (url) URL.revokeObjectURL(url); };
  }, [language, config]);
  return <div>
    <p><strong>{prompt && !failed ? `Approved cached ${config?.display_name} instruction · prerecorded AI voice` : 'Text-only confirmation · voice unavailable or unapproved.'}</strong></p>
    <p dir={config?.direction === 'rtl' ? 'rtl' : 'ltr'} lang={config?.language_code}>{config?.text}</p>
    {prompt && !failed ? <><Player url={prompt.url} onError={() => setFailed(true)} />
      <p className="speech-note">{prompt.attribution} Generated {prompt.generated}. This fixed instruction does not read the selected transcript.</p></>
      : <p className="speech-note">Configured voice ID is not verification. Caption and pronunciation require manual language/listening approval before playback.</p>}
  </div>;
}
