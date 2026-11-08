import catalog from '../../../../shared/tts_prompts.json';

export const TTS_MODEL = catalog.model_id;
export const PROMPT_REVISION = catalog.prompt_revision;
export const TTS_ATTRIBUTION = 'AI-generated with ElevenLabs; UNHEARD-authored demo instruction, not the FLEURS speaker.';
export function recoveryPrompt(language: string) {
  return Object.hasOwn(catalog.languages, language) ? catalog.languages[language as keyof typeof catalog.languages] : null;
}
