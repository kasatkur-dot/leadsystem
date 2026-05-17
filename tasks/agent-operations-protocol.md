# Agent Operations Protocol

Date: 2026-04-30
Project: Lead Intelligence Pipeline, ООО «Вектор Плюс-Про»

## Simple Explanation

This is a multi-agent system.

In the lesson/management model, the chief orchestrator is `CLAUDE.md`.
It is the top rule file that tells people and AI assistants how the project works.

The Python file `orchestrator/scheduler.py` is lower in the hierarchy.
It is the technical runner: it starts agents when the system is running.

The agents do not talk to each other like people in a chat. They work through:

- the chief project orchestrator: `CLAUDE.md`;
- the runtime runner: `orchestrator/scheduler.py`;
- Redis queues;
- shared models;
- logs;
- Bitrix24;
- Telegram notifications;
- project files.

## Hierarchy

There is one chief project orchestrator and one runtime runner.

They are not the same level.

```text
CLAUDE.md
  ↓ chief project orchestrator: rules, roles, architecture, repair protocol
REPORT.md
  ↓ current state and work log
orchestrator/scheduler.py
  ↓ runtime technical runner when the system runs
Redis queues
  ↓ data dispatcher between agents
agents/*
  ↓ 6 worker agent departments and subagents
Bitrix24 / Telegram
  ↓ business output and human control
```

Full agent map:

```text
agents/
├── agent1_scout      market and competitor intelligence, Wave 2
├── agent2_collector  lead collection, Wave 1+
├── agent3_processor  cleaning, enrichment, scoring, offer generation, Wave 1
├── agent4_publisher  content and publishing, Wave 1-3
├── agent5_crm        Bitrix24, notifications, admin/reporting, Wave 1
└── agent6_outreach   Telegram/social outreach, Wave 1-3
```

Current runtime MVP map:

```text
orchestrator/scheduler.py currently starts:
├── Agent 2: tender_collector
├── Agent 3: processor
├── Agent 5: crm_router
└── Agent 6: tg_monitor, approver, sender, relevance_pipeline

Agent 1 and Agent 4 are present in the project structure, but not yet active in the runtime schedule.
```

## Who Is Main In Which Sense

There are different "main" roles.

| Role | In our project | What it means |
|---|---|---|
| Chief project orchestrator | `CLAUDE.md` | Highest local rule file: roles, architecture, constraints, update rules, repair protocol |
| Technical runtime runner | `orchestrator/scheduler.py` | Starts agents, schedules jobs, catches job errors |
| Data dispatcher | Redis queues | Moves leads between agents |
| Human/project registrar | `REPORT.md` | Records what is done, broken, checked, and next |

Short answer:

```text
Chief orchestrator = CLAUDE.md.
Runtime runner = orchestrator/scheduler.py.
Data dispatcher = Redis.
Project registrar = REPORT.md.
Business destination = Bitrix24.
Human control point = manager via Telegram/Bitrix.
```

## Why This Is Not Two Conflicting Bosses

`CLAUDE.md` is the main orchestrator file for people and AI assistants.
It says how the project should be understood, changed and documented.

`orchestrator/scheduler.py` is the running Python process.
It starts agents and schedules jobs when the lead system is launched.

So the hierarchy is:

```text
CLAUDE.md commands the project logic.
orchestrator/scheduler.py executes the launch schedule.
REPORT.md records what happened.
```

## Agent Roles

| Agent | Role | If it breaks |
|---|---|---|
| Agent 1 Scout | Market and competitor intelligence | Non-critical for MVP, pause and inspect later |
| Agent 2 Collector | Collects raw leads | Check source credentials, source access, Redis raw queue |
| Agent 3 Processor | Cleans, enriches, scores, creates offer | Check models, Claude API, parsing, scoring logs |
| Agent 4 Publisher | Posts content and updates channels | Check platform credentials, content, posting rules |
| Agent 5 CRM Router | Sends leads to Bitrix24 and notifies manager | Check Bitrix webhook, Telegram bot token, CRM logs |
| Agent 6 Outreach | Monitors chats, prepares replies, waits for approval, sends | Check Telethon sessions, approver, sender, Redis outreach queues |

## How To Fix One Broken Agent

Do not go directly to the broken agent as the normal workflow.
Start from the chief orchestrator/protocol, then diagnose the exact agent.

Hard repair rule:

```text
Before fixing anything, read REPORT.md and CLAUDE.md.
Identify which agent is broken.
Do not rewrite the whole system.
Check logs, .env, Redis, and that agent's queue.
Fix only the smallest broken part.
After verification, update REPORT.md.
```

Use this order:

1. Read `REPORT.md`.
2. Read the relevant rule in `CLAUDE.md`.
3. Identify which agent failed.
4. Check logs.
5. Check required `.env` values.
6. Check Redis is running.
7. Check the queue for that agent.
8. Run only the broken agent/module in isolation if possible.
9. Fix only the smallest broken part.
10. Run one test scenario.
11. Update `REPORT.md`.

## Where To Look First

| Symptom | First place to check | Likely owner |
|---|---|---|
| No leads collected | Source credentials, Agent 2, Redis raw queue | Agent 2 |
| Leads collected but not scored | Agent 3 logs, Claude API key, raw queue | Agent 3 |
| Lead scored but not in Bitrix | Bitrix webhook, Agent 5 logs, qualified queue | Agent 5 |
| No Telegram notifications | Telegram bot token, manager chat id, Agent 5 notifier | Agent 5 |
| Telegram chats not monitored | Telethon session, `tg_monitor`, target chats | Agent 6 |
| Reply not sent after approval | `approver`, `sender`, `outreach:approved`, sender session | Agent 6 |
| Duplicate leads appear | Agent 3 cleaner and fingerprint logic | Agent 3 |
| Wrong offer or score | Agent 3 scorer/offer prompt and test examples | Agent 3 |
| Whole system silent | Orchestrator, Redis, `.env`, logs | Orchestrator |

## Should We Talk To One Agent Directly?

For humans:

```text
Do not "talk to Agent 3" directly as the normal workflow.
Talk to the project through the orchestrator/protocol:
REPORT.md -> CLAUDE.md -> logs -> exact agent/module -> isolated test -> fix -> REPORT.md.
```

For debugging:

it is okay to test one agent directly, but only after identifying the problem.

Example:

```text
Problem: leads are not going to Bitrix.
Do not change Telegram or tender code.
Check Agent 5 only: Bitrix webhook, qualified queue, crm_router logs.
```

## Current Gap

The current orchestrator logs errors, but it is not yet a full admin/control center.

Missing or future-needed:

- admin bot commands: `/status`, `/pause`, `/restart`, `/logs`;
- health checks per agent;
- retry queue for failed Bitrix/Gmail/Telegram calls;
- per-agent status summary;
- alert when an agent is silent for too long;
- dashboard or weekly report.

This is why `agent5_crm/admin_bot` and `stats_reporter` are important later.

## Minimal Control System For MVP

Before full admin bot, use this simple control model:

| Control item | MVP method |
|---|---|
| What is current state? | `REPORT.md` |
| What is running? | orchestrator logs |
| Are queues moving? | Redis queue sizes |
| Did a lead reach sales? | Bitrix24 + Telegram manager alert |
| Did an agent fail? | logs + orchestrator error |
| What changed after fix? | update `REPORT.md` |

## Rule For Future Development

Every agent should eventually have:

- clear input queue/source;
- clear output queue/destination;
- required `.env` values;
- one manual test case;
- one failure case;
- log messages that show what happened;
- status visible through admin bot or report.

## Next Small Step

For now, continue with `.env` and MVP launch.

Before expanding sources, add the missing first-touch fields to lead models:

- `source_type`;
- `first_touch_channel`;
- `consent_status`;
- `next_action`;
- `proof_needed`;
- `landing_needed`;
- `lead_magnet_path`;
- `sla`.
