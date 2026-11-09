import { useEffect, useId, useRef, useState } from 'react';
import './audio-waveform.css';

const waveformUnavailable = 'Waveform unavailable. Use the audio controls.';

// Equal time bins of peak amplitude across every channel; no synthetic bars.
export function waveformPeaks(channels: Float32Array[], bins = 160): number[] {
  const length = channels[0]?.length ?? 0;
  if (!length) return [];
  return Array.from({ length: Math.min(bins, length) }, (_, bin) => {
    const start = Math.floor(bin * length / Math.min(bins, length));
    const end = Math.floor((bin + 1) * length / Math.min(bins, length));
    let peak = 0;
    for (const channel of channels) for (let i = start; i < end; i++) peak = Math.max(peak, Math.abs(channel[i]));
    return peak;
  });
}

export default function AudioWaveform({ src, label, onError }: { src: string; label: string; onError?: () => void }) {
  const audio = useRef<HTMLAudioElement>(null);
  const clipId = useId().replace(/:/g, '');
  const [peaks, setPeaks] = useState<number[]>([]);
  const [waveStatus, setWaveStatus] = useState('Loading waveform…');
  const [state, setState] = useState('Ready');
  const [position, setPosition] = useState({ time: 0, duration: 0 });
  const [failed, setFailed] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [volume, setVolume] = useState({ level: 1, muted: false });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let context: AudioContext | undefined;
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setPeaks([]); setWaveStatus('Loading waveform…'); setFailed(false);
    setPosition({ time: 0, duration: 0 }); setState('Ready'); setPlaying(false);
    void (async () => {
      try {
        if (!window.AudioContext) throw new Error('Web Audio unavailable');
        const response = await fetch(src, { signal: controller.signal });
        if (!response.ok) throw new Error('Audio unavailable');
        const bytes = await response.arrayBuffer();
        if (!active) return;
        context = new AudioContext();
        const buffer = await context.decodeAudioData(bytes);
        if (!active) return;
        setPeaks(waveformPeaks(Array.from({ length: buffer.numberOfChannels }, (_, i) => buffer.getChannelData(i))));
        setWaveStatus('');
      } catch { if (active) setWaveStatus(waveformUnavailable); }
      finally { window.clearTimeout(timeout); if (context && context.state !== 'closed') void context.close(); }
    })();
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [src]);

  useEffect(() => {
    const player = audio.current;
    if (!player) return;
    let frame = 0;
    const update = () => {
      setPosition({ time: player.currentTime, duration: Number.isFinite(player.duration) ? player.duration : 0 });
    };
    const tick = () => { update(); if (!player.paused && !player.ended) frame = requestAnimationFrame(tick); };
    const play = () => { cancelAnimationFrame(frame); setState('Playing'); tick(); };
    const pause = () => { cancelAnimationFrame(frame); update(); setPlaying(false); setState(player.ended ? 'Ended' : 'Paused'); };
    const waiting = () => { cancelAnimationFrame(frame); update(); setState('Loading audio…'); };
    const ready = () => { update(); if (player.paused) setState(player.ended ? 'Ended' : player.currentTime > 0 ? 'Paused' : 'Ready'); };
    const updateVolume = () => setVolume({ level: player.volume, muted: player.muted });
    const events = { timeupdate: update, durationchange: update, loadedmetadata: update, seeking: update, seeked: ready, canplay: ready,
      play: () => setPlaying(true), playing: play, pause, ended: pause, waiting, loadstart: waiting, volumechange: updateVolume };
    for (const [event, handler] of Object.entries(events)) player.addEventListener(event, handler);
    return () => {
      for (const [event, handler] of Object.entries(events)) player.removeEventListener(event, handler);
      cancelAnimationFrame(frame); player.pause();
    };
  }, [src]);

  function startPlayback() {
    const player = audio.current;
    if (player?.paused) {
      void player.play().catch(error => {
        if (error?.name !== 'AbortError') setState('Could not play audio. Try again.');
      });
    }
  }

  const progress = position.duration ? Math.min(1, position.time / position.duration) : 0;
  const amplitudeScale = Math.max(...peaks, .000001);
  const seekLabel = `Playback position for ${label}`;
  return <div className="audio-waveform" data-playback-state={failed ? 'Unavailable' : state}>
    <audio ref={audio} controls={waveStatus === waveformUnavailable} hidden={waveStatus !== waveformUnavailable || failed}
      preload="metadata" src={src} aria-label={label} onError={() => { setFailed(true); onError?.(); }} />
    {failed ? <p role="status">Audio unavailable or unsupported in this browser. Saved transcripts remain available.</p> : <>
      {peaks.length ? <div className="waveform-controls">
        <button type="button" className="waveform-play" aria-label={playing ? 'Pause recording' : 'Play recording'}
          disabled={!position.duration} onClick={() => { if (audio.current?.paused) startPlayback(); else audio.current?.pause(); }}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
            {playing ? <path d="M7 5h4v14H7zm6 0h4v14h-4z" /> : <path d="M8 5v14l11-7z" />}
          </svg>
        </button>
        <div className="waveform-track" title="Recording amplitude, scaled to its peak">
        <svg viewBox="0 0 640 64" preserveAspectRatio="none" aria-hidden="true">
          <defs><clipPath id={clipId}><rect width={640 * progress} height="64" /></clipPath></defs>
          <g className="waveform-unplayed">{peaks.map((peak, i) => <rect key={i} x={i * 640 / peaks.length} y={32 - peak / amplitudeScale * 30} width={640 / peaks.length - 1} height={Math.max(.5, peak / amplitudeScale * 60)} />)}</g>
          <g className="waveform-played" clipPath={`url(#${clipId})`}>{peaks.map((peak, i) => <rect key={i} x={i * 640 / peaks.length} y={32 - peak / amplitudeScale * 30} width={640 / peaks.length - 1} height={Math.max(.5, peak / amplitudeScale * 60)} />)}</g>
          <line x1={640 * progress} x2={640 * progress} y1="0" y2="64" className="waveform-cursor" />
        </svg>
        <input type="range" aria-label={seekLabel} min="0" max={position.duration || 1} step="0.01" value={position.time}
          disabled={!position.duration} onClick={startPlayback}
          onChange={event => { if (audio.current) { audio.current.currentTime = Number(event.target.value); setPosition({ ...position, time: Number(event.target.value) }); } }} />
        </div>
      </div> : <p className="speech-note" role="status">{waveStatus}</p>}
      <div className="waveform-toolbar">
        <p className="audio-status"><span role="status">{state}</span><span aria-hidden="true"> · {position.time.toFixed(1)} / {position.duration.toFixed(1)} s</span></p>
        {peaks.length ? <div className="waveform-volume">
          <button type="button" onClick={() => {
            const player = audio.current;
            if (!player) return;
            if (player.volume === 0) { player.volume = 1; player.muted = false; }
            else player.muted = !player.muted;
          }}>{volume.muted || volume.level === 0 ? 'Unmute' : 'Mute'}</button>
          <input type="range" aria-label="Volume" min="0" max="1" step="0.01" value={volume.muted ? 0 : volume.level}
            onChange={event => {
              if (!audio.current) return;
              audio.current.volume = Number(event.target.value);
              audio.current.muted = false;
            }} />
        </div> : null}
      </div>
    </>}
  </div>;
}
