# Local four-act demonstration runbook

**Status:** proposed judging flow; actual steps/assets/metrics must be filled in after implementation. Team handles the video, Devpost and submission (D-024).

## Before judge arrives

1. Start backend and frontend on localhost using the commands documented by T-001; leave terminal logs accessible for diagnostics.
2. Verify `GET /health`, static JSON schema version, corrected Ward 10 data, and one playable licensed sample.
3. Verify last actual ElevenLabs results load, and cached demo mode works with the backend disconnected.
4. Verify the key and `.env` are not displayed in a browser, terminal recording or repository.
5. Prepare one **verified** Urdu sample whose transcriptions and CER are actually measured, and know whether it improved/worsened/tied. Do **not** script an unsupported positive result.

## Approximate 3–4 minute narrative (adjust for the event format)

| Act | Spoken story | Interface action | Claim boundary |
|---|---|---|---|
| 1. Discover | In this supplied pack, eight tracked language categories lack labelled task-request audio. Together they account for 79,940 home-language speakers. | select Urdu, show corrected census wards, count/share | no claim of 79,940 residents failing with AI |
| 2. Investigate | We processed authentic FLEURS recordings with ElevenLabs, and checked baseline vs correct-language guidance. | play verified Urdu clip; compare reference/auto/guided; show per-language aggregate and n | speakers are **not** identified as Mississauga residents; result is exploratory |
| 3. Demonstrate | Instead of acting on unconfirmed text, the prototype reads it back and asks for confirmation. | show confirmed or rejected path, one retry and referral; use generated voice if available | judge response to third-party audio is simulated; no live 311 handoff |
| 4. Recommend | Use language gaps and actual ward speaker populations to prioritize **future data collection**. | show Urdu testing recommendation and wards by absolute count/share | no ward-level ASR failure forecast |

## If things go wrong

- **Internet/API down:** announce 'saved, previously generated experiment results'; continue map/speech lab/recommendations.
- **Guided model unsupported:** show source-grounded unsupported status; do not use expected result placeholder.
- **TTS unavailable:** use cached generated voice if verified or display textual confirmation, clearly labelled.
- **Polygon mismatch:** use ward chart (do not claim map is validated).
- **No measured sample ready:** do not fake ElevenLabs transcripts. Demo available census evidence only and openly state experiment is unfinished.

## Honest Q&A answers

- **Why a map?** Census tells us where communities are concentrated, guiding outreach for future studies; it does not locate speech failures.
- **Are these residents unable to use English?** No; home language does not imply English proficiency.
- **Does language guidance work?** State the real per-language pilot counts and uncertainty; if unsupported/inconclusive, say that.
- **Is this 311-ready?** No: prototype for evaluation priorities and a basic user-confirmation safeguard, not routing/production use.
- **Why not an Agent?** Deterministic verification and reproducible measurements matter more than autonomous conversation in this MVP.

## Completion evidence

Record who ran the full demo, starting instructions, observed errors, fixes, and exactly which experimental results were shown. Never mark rehearsal passed merely because a slide/script was written.
