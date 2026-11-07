# Roadmap — dependency-based, scope-frozen MVP

**No estimate here is a promise about remaining hackathon time.** Prioritize verified research and a dependable localhost demo. D-024 reserves submission work to the human team.

## Milestone M0 — Contract and source preflight

1. **T-001** project bootstrap/repo/scripts skeleton and local run commands.
2. **T-002** source audit, licenses, data directories and provenance checks.
3. **T-003** v1 schemas, language/ward identifiers and fixtures.

**Exit:** Both developers can load one contract-valid example through the same local app setup; missing/unsupported states are specified, no fabricated research results.

## Milestone M1 — One real vertical slice (top priority)

1. **T-004** corrected census aggregation; **T-005** request coverage and ranking.
2. **T-007** deterministic FLEURS sampling + manifest.
3. **T-008** one authentic ElevenLabs Scribe preflight, validating actual response/configs.
4. **T-006** verified ward boundaries (can proceed in parallel with speech work).
5. **T-010** reusable CER/WER logic and a real preflight clip export; **T-011** minimal map and **T-013** speech comparison with **one real Urdu clip**.

**Exit:** One ward, Urdu, one real clip, both modes if supported, accurate metrics, working demo path. Do not implement a fake successful-guidance fixture as the final result.

## Milestone M2 — Full controlled pilot & visualization

1. **T-009** 48-clip planned experiment with request caching, explicit partial/failed statuses.
2. Re-run the **T-010** metric/export utilities on all actual results produced by T-009; keep incomplete pairs explicit.
3. **T-012** global selector and all missing-data state rules.
4. **T-016** language-first recommendations and ward focus.

**Exit:** Corrected ward map, source-grounded coverage insights, all actually processed pilot data, limitations and data-availability labels.

## Milestone M3 — One safe recovery demonstration

1. **T-014** deterministic FastAPI confirmation/retry/referral state machine.
2. **T-015** guided prerecorded UI, ElevenLabs TTS preflight and cached prompt.

**Exit:** Works locally with controlled inputs and no fake human handoff. Saved authentic results remain accessible offline.

## Milestone M4 — Integration, tests and demo freeze

1. **T-017** regression and CI checks; **T-018** full demo / outage rehearsal.
2. **T-019** citations and redistribution audit; **T-020** usability and integration polish (strict time cap).

**Exit:** Two developers can independently run localhost four-act demo from a clean checkout/environment. Freeze new features and document gaps.

## Parallel work and handoffs

| Developer 1 | Developer 2 | Shared handoff |
|---|---|---|
| T-002, 004, 005, 007–010, 014 | T-006, 011–013, 015, 016, 020 | T-001, 003, 017–019 |

**Checkpoint A:** M1, first real end-to-end Urdu slice. **Checkpoint B:** M2/M3, all four MVP modules accessible. **Checkpoint C:** M4, release-ready local demo after failure tests.

## Stop rules when blocked

- **No geo polygon match:** fall back to labelled ward chart/table; never fake choropleth geometry.
- **No guided API support:** retain auto results, report guided unsupported; never infer an effect.
- **Credit/billing/API failure:** stop new requests, use existing real cached experiments; report actual coverage/paired n.
- **TTS unavailable:** use verified cached voice clip or textual clarification; label missing voice functionality.
- **Insufficient time:** protect verified data and ElevenLabs experiments, then clean explanatory UI; cut stretch features and animation.

## Not in roadmap until approved

Neighbourhood map, live mic, authentication, public Cloudflare/backend hosting, agentic LLM, Gemini, accent study, municipal service routing.
