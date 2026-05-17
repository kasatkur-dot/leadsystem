# Wave 1 MVP Launch Table

Date: 2026-04-29
Status: final logic table before continuing development
Project: Lead Intelligence Pipeline, ООО «Вектор Плюс-Про»

## Decision

Wave 1 is not "all possible lead sources".

Wave 1 is the smallest set of channels where:

- demand already exists;
- first contact is clear;
- a manager can react quickly;
- the source can be routed into Bitrix24;
- the system can be tested without building every future channel.

## Wave 1 Sources

| Priority | Source | Segment | Signal | First touch | Auto reply allowed | Who answers | Destination | SLA | Trust proof | Launch status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gmail tender folder | B2B engineering | Tender / request for проектирование, РД, конструктив | Email, call, КП | No | Manager | Bitrix24 + TG alert | Same day | SRO, cases, example КП, team expertise | After `.env` + Gmail app password |
| 2 | Telegram chats | B2C + B2B | Public question about перепланировка, согласование, проект, конструктив | Helpful human-style comment | Only after approval | Approver + sender | Outreach queue -> Bitrix24 if interest | Candidate review within 30 min | Short expert answer, no spam, case/link later | After Telethon auth |
| 3 | Profi.ru | B2C + small B2B | Client posts job request | Platform response | No | Manager manually first | Bitrix24 manually first | Fast response, ideally within 1 hour | Profile, reviews, clear offer | Reactivate manually before automation |
| 4 | Yandex Services | B2C + small B2B | Client posts job request | Platform response | No | Manager manually first | Bitrix24 manually first | Same day, faster for hot requests | Profile, reviews, clear offer | Reactivate manually before automation |
| 5 | Avito | B2C + B2B | Message to listing / relevant service request | Avito chat | No | Manager manually first, automation later | Bitrix24 after qualification | Same day | Listing quality, price range, cases | Check listings before collector |
| 6 | Yandex Maps card | Local B2C/B2B | Search, call, route, message from card | Card, phone, messenger, website | No | Manager | Bitrix24 manually first | During business hours | Reviews, photos, services, address, cases | Must configure, current leak |
| 7 | Old clients / old inquiries | B2C + B2B + partners | Past client or old request can refer/reopen | Personal message/call | No | Manager | Bitrix24 reactivation list | Batch weekly | Past work, referral offer, trust already exists | Start manually |

## What Is Not Wave 1 Yet

| Source | Why not first |
|---|---|
| 2GIS API/search | Useful, but first fix Yandex Maps and first-contact routing |
| HH vacancy signals | Strong pre-demand signal, but needs careful filtering |
| Commercial real estate listings | Useful, but harder to attribute and contact cleanly |
| Developer databases / procurement pages | Good B2B long-cycle source, not fast MVP |
| Competitor review monitoring | Useful intelligence, not first launch dependency |
| Full website build | Needed, but should not block the first working lead paths |
| Full partner program | Needed, but first define offer and tracking |

## Required Lead Fields Before Next Development Layer

These fields should be added to the lead model or preserved in metadata before expanding collectors:

| Field | Why it matters |
|---|---|
| `source_type` | Direct request, pre-demand signal, partner, trust surface, owned base |
| `first_touch_channel` | Email, platform reply, public comment, private message, call, form, partner intro |
| `consent_status` | Inbound request, public source, partner referral, manual review required |
| `next_action` | Reply, call, КП, ask for docs, partner follow-up, archive |
| `proof_needed` | Case, SRO, review, price range, document list, example КП |
| `landing_needed` | Whether this source needs a page/link to convert |
| `lead_magnet_path` | None, ПРОВЕРКА, tender review, document checklist, price range |
| `sla` | How fast manager should react |

## Manual Test Before Development

Before adding the next collector, run a paper test with 10 leads:

| Test group | Count |
|---|---:|
| Tenders | 3 |
| Telegram messages | 3 |
| Off-target/noise | 2 |
| Duplicate | 1 |
| Partner/referral | 1 |

For each lead, fill:

```text
source
source_type
first_touch_channel
consent_status
flow
score
next_action
destination
proof_needed
lead_magnet_path
```

## Final Gate

Development can continue after:

- `.env` is filled;
- Telegram sessions are authorized;
- Redis is running;
- Wave 1 table is accepted;
- the model gap is acknowledged: leads must store first touch, consent, next action and trust path.

## Next Small Step

Continue filling `.env`, then run Telegram/tender MVP checks.
