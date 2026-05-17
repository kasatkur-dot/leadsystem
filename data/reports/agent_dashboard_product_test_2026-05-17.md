# Agent Dashboard Product Test — 2026-05-17

## Scope

Проверка текущего продукта многоагентной системы:

- backend `backend/agent_dashboard_api`;
- frontend `frontend/agent-system-visual`;
- локальный dashboard на `http://127.0.0.1:8788/`;
- agent-control chat в режиме `openrouter_free_test`.

Проверку выполняли:

- main Codex test pass;
- backend tester subagent;
- frontend tester subagent;
- Playwright UI pass.

## Safety

Не запускались:

- Redis;
- Bitrix24;
- Telegram;
- IMAP;
- scheduler;
- publisher;
- Whisper;
- image generation;
- embeddings;
- массовый сбор;
- реальные публикации;
- outreach.

Внешние вызовы выполнялись только для локального agent-control text chat через OpenRouter free model `deepseek/deepseek-v4-flash:free`.

## Backend Results

| Check | Result |
|---|---|
| `GET /api/health` | OK |
| `GET /data.js` | OK |
| `GET /api/dashboard` | OK |
| `GET /api/agent-system-data` | OK |
| CORS preflight `OPTIONS /api/agent-control/chat` | OK |
| unknown POST endpoint | JSON `404`, not HTML |
| `POST /api/agent-control/chat` manage/default/develop/marketing | OK, live OpenRouter text response |
| `POST /api/agent-control/knowledge-search` | dry-run, `DRY_RUN_NOT_EMBEDDED` |
| `POST /api/agent-control/image` | dry-run, `DRY_RUN_IMAGE_NOT_GENERATED` |
| `POST /api/agent-control/voice` | dry-run, `DRY_RUN_NOT_TRANSCRIBED` |

Current backend data:

| Metric | Value |
|---|---:|
| agents | 6 |
| subroles | 33 |
| services | 7 |
| artifacts | 29 |
| visual nodes | 47 |
| scenarios | 4 |
| edges | 54 |
| runtime mode | `openrouter_free_test` |
| provider | `openrouter` |
| live text LLM | true |

## Frontend Results

| Check | Result |
|---|---|
| page load | OK |
| browser console | no errors, only Babel dev warning |
| graph render | OK, 6 agents visible |
| zoom / center buttons | visible |
| inspector | OK for Agent 3 and Agent 5 |
| scenario playback | OK: scenario switch, Play, Reset work |
| chat dock | OK: message sends, response appears |
| chat readability | improved: bigger bottom dock, scrollable history |
| HTML instead of JSON bug | fixed |

## Found And Fixed During Test

1. `Unexpected token '<'` happened when frontend got HTML instead of JSON.
   Fixed by routing local API calls to `http://127.0.0.1:8788` when needed and by adding content-type validation.

2. CORS preflight had duplicated `Access-Control-Allow-Origin`.
   Fixed in `backend/agent_dashboard_api/server.py`.

3. Chat dock was too small.
   Fixed in `frontend/agent-system-visual/styles.css`.

4. Agent-control model invented generic roles instead of the real 6 agents.
   Fixed in `backend/agent_dashboard_api/agent_control.py` by passing `known_project_agents` from dashboard into the live LLM prompt.
   Retest result: the model listed exactly Agent 1 Scout, Agent 2 Collector, Agent 3 Processor, Agent 4 Publisher, Agent 5 CRM, Agent 6 Outreach.

## Current Product Stage

The product currently works up to:

```text
local dashboard -> real agent map -> inspector -> scenario playback -> local chat command -> OpenRouter free text response -> safe handoff preview
```

It does not yet execute the full operational chain:

```text
real command -> Redis queue -> real agent execution -> Bitrix24/Telegram/publisher/action -> analytics update
```

## What Works Now

- A human can open the local dashboard.
- The system shows the real 6-agent structure.
- The system shows subroles, artifacts, scenarios and safety locks.
- Inspector exposes OKR/KR/inputs/outputs for agents.
- Scenario playback demonstrates the expected workflow.
- Chat command center accepts text commands.
- OpenRouter free model can answer inside the local UI.
- The backend protects all non-text integrations as dry-run.

## What Is Dry-Run Or Not Ready

- Voice transcription is not active.
- Image generation is not active.
- Knowledge search / embeddings are not active.
- Redis queue execution is not started from dashboard.
- Bitrix24 and Telegram are not called from dashboard.
- Scheduler and publisher are not started from dashboard.
- Agent-control chat creates a response and handoff preview, but does not yet execute real tasks.

## Risks / Gaps

| Risk | Status |
|---|---|
| `health.external_calls.llm=false` can confuse because chat can call OpenRouter when live mode is on | Needs wording cleanup |
| mobile `390x844` layout has overflow in inspector/scenario area | Needs fix |
| scenario buttons are too compressed on mobile | Needs fix |
| frontend still uses CDN/Babel MVP mode | Needs Vite/React build before production/demo handoff |
| agent-control prompt is better now, but still should become stricter and more deterministic | Next step |

## Verdict

Current state: internal MVP / technical demo ready.

Not ready yet for production or external client demo.

The next engineering step is to harden agent-control responses and mobile layout before any server publication.
