# Deep Traffic Source Audit

Date: 2026-04-29
Status: strategic audit before continuing development
Project: Lead Intelligence Pipeline, ООО «Вектор Плюс-Про»

## Core Finding

The current system already covers the obvious channels: tenders, Telegram, Profi.ru, Yandex Services, Avito, maps, partners, CRM.

What was underweighted:

1. Pre-demand signals: events before the client asks for a project.
2. Trust surfaces: places where a client checks whether the company is real.
3. Partner sources around the project lifecycle.
4. Existing and past contacts.
5. A simple website/landing layer as the receiving point for all traffic.

## Traffic Layers

### Layer 1. Existing Demand

These sources contain people or companies already asking for work.

| Source | Demand type | First contact | Priority |
|---|---|---|---|
| Gmail tender folder | B2B, tender already exists | Email / КП / call | Start now |
| Commercial tender platforms | B2B, formal procurement | Platform bid / КП | Start after Gmail |
| Profi.ru | B2C/B2B service request | Platform response | Start manually now |
| Yandex Services | B2C/B2B service request | Platform response | Start manually now |
| Avito | Service request / message to listing | Avito chat | Start after profiles are checked |
| Telegram/VK questions | Problem voiced in public | Helpful approved answer | Start after Telegram auth |

### Layer 2. Pre-Demand Signals

These are not requests yet, but they show that project work may soon be needed.

| Source | Signal | Why it matters | Priority |
|---|---|---|---|
| Building permits / construction registries | New construction/reconstruction | Project work exists before and around permits | Add to map now, automate later |
| Developer databases / ERZ / nash.dom.rf | Developers and active projects | B2B target list for long-cycle sales | Add to CRM research |
| Commercial real estate listings | Business buys/rents premises | Fit-out, layout, project documentation may follow | Wave 2 |
| Business openings in maps/social/news | New salon, clinic, restaurant, office | Often needs project, layout, signage, ventilation | Wave 2 |
| HH vacancies | Hiring architect/constructor/project engineer | Company has project load or lacks internal capacity | Wave 2 |
| Franchise expansion | New branch planned | Standard project and approvals often needed | Wave 3 |
| Competitor negative reviews | Client pain and dissatisfaction | Can reveal unmet demand and weak spots | Wave 3 |

### Layer 3. Trust and Conversion Surfaces

These may not generate demand alone, but they decide whether the person trusts us after the first touch.

| Surface | Role | Must account for now |
|---|---|---|
| Yandex Maps card | Local trust, calls, route, reviews, service list | Yes |
| 2GIS card | Local trust and business discovery | Yes, after Yandex |
| Website / landing pages | Proof, cases, forms, lead magnet, partner links | Yes |
| Case pages | Show expertise and reduce fear | Yes |
| Reviews | Social proof | Yes |
| Telegram/MAX/VK content | Warms and educates | Yes, but not instead of lead capture |

### Layer 4. Partner Sources

These are often better than cold traffic because the client already trusts someone.

| Partner | Client moment | First contact | Priority |
|---|---|---|---|
| Realtors / agencies | Sale, purchase, mortgage issue | Referral | Wave 1-2 |
| Mortgage brokers | Bank sees перепланировка/document risk | Referral | Wave 2 |
| Real estate lawyers | Deal is blocked by documents | Referral | Wave 2 |
| Designers | Before repair/project implementation | Referral | Wave 1-2 |
| Fit-out contractors | Business opens or repairs premises | Referral | Wave 2 |
| Signage/ventilation/fire safety contractors | Business needs premises adapted | Referral | Wave 2 |
| BTI/cadastral/legal offices | Client needs legalization/documents | Referral | Wave 2 |
| Facility managers / управляющие компании | Reconstruction/repair in commercial asset | Referral | Wave 2 |
| Developers/general contractors | Need subcontract/project capacity | Relationship sale | Wave 3 |

### Layer 5. Owned Base

This is easy to forget, but it can be the cheapest source.

| Source | What to do |
|---|---|
| Past clients | Ask for referrals, reviews, repeat projects |
| Old inquiries | Re-score and reactivate |
| Existing tender contacts | Add to CRM and follow up |
| Existing partner acquaintances | Formalize referral offer |
| Existing content/library | Convert into posts and lead magnet paths |

## What We Should Add to the System Map

These should be included before development goes too far:

1. `source_type`: direct_request / pre_demand_signal / partner / trust_surface / owned_base.
2. `first_touch_channel`: email / platform_reply / public_comment / private_message / call / form / partner_intro.
3. `consent_status`: public_source / inbound_request / partner_referral / manual_review_required.
4. `next_action`: reply / call / КП / ask_for_docs / partner_follow_up / archive.
5. `proof_needed`: case / license-SRO / price_range / review / document_list / example КП.
6. `landing_needed`: yes/no.
7. `lead_magnet_path`: none / ПРОВЕРКА / tender_review / document_checklist / price_range.

## Revised Logical Priority

### Start immediately

1. Gmail tender folder.
2. Telegram chats with approval.
3. Profi.ru and Yandex Services manual reactivation.
4. Yandex Maps card setup.
5. Old clients and old inquiries.

### Build next

1. Website/landing structure for two flows.
2. Lead magnet `ПРОВЕРКА перепланировки`.
3. Partner referral list and offer.
4. Avito profile and response pipeline.
5. Commercial tender platform monitoring beyond email.

### Add after first data

1. 2GIS search/API.
2. HH vacancy signals.
3. Commercial real estate signals.
4. Developer databases and procurement pages.
5. Competitor review monitoring.

## Website and Lead Magnet Decision

Website: needed.

Reason: without a site or focused landing pages, traffic from maps, partners, posts, ads and lead magnets has no stable place to land. The website is not the first source of all leads, but it is the trust and capture layer.

Lead magnet: needed.

Reason: direct hot leads are not enough. Many people are scared, unsure, or comparing options. The lead magnet gives them a low-risk first step.

Best first lead magnet:

```text
ПРОВЕРКА перепланировки
```

Best B2B lead magnet:

```text
Экспресс-разбор тендера / ТЗ
```

What not to do:

- Do not start with a generic ebook.
- Do not build a huge site before running the first lead paths.
- Do not hide the manager behind a long bot.

## Strategic Recommendation

The system should be built as a radar plus trust funnel:

```text
Radar finds demand signals -> first touch happens in the native channel -> Bitrix records the lead -> site/lead magnet supports trust -> manager closes the conversation.
```

This means development must not only create collectors. It must also store the first-touch logic and the next action for each source.

## Sources Used

- B2B-Center has active project/design tenders and formal participation through registration/tariffs: https://www.b2b-center.ru/search-tender/tendery-proektirovanie/
- KomTender shows a category for project works in construction and building networks: https://www.komtender.ru/category/project
- 2GIS Directory API can search organizations by activity/category/city and display organization data: https://dev.2gis.ru/catalog/
- Yandex Business supports user заявки from organization cards and provides contact fields for requests: https://yandex.ru/support/business-priority/ru/manage/form
- Yandex Business explains that organization cards in Maps help attract clients and that fuller cards rank better in Search and Maps: https://yard.yandex.ru/courses/yandex-karty-dlya-biznesa/zachem-nuzhny
- HeadHunter has an official API and OAuth/documentation for vacancy and employer data: https://dev.hh.ru/
- ERZ describes itself as a database of housing developers and new buildings: https://erzrf.ru/map
- Минстрой has open data for construction permits: https://minstroyrf.gov.ru/opendata/7707780887-reestrstroit/
- HubSpot notes that lead generation forms turn website visitors into leads and should create a good experience: https://blog.hubspot.com/marketing/cta-vs-form-blog-conversion-test
- B2B website lead generation guidance recommends starting with one relevant content offer and contextual follow-up instead of building everything at once: https://www.trajectorywebdesign.com/blog/b2b-website-lead-gen/
