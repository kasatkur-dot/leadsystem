# Traffic and First Touch Map

Date: 2026-04-29
Status: research decision before continuing development
Project: Lead Intelligence Pipeline, ООО «Вектор Плюс-Про»

## Main Decision

The system must not only collect leads. It must understand where the first contact happens.

Simple formula:

```text
Traffic source -> demand signal -> first touch -> raw lead -> scoring -> Bitrix24 -> manager action
```

If we do not define the first touch, the system will collect noise instead of real opportunities.

## First Wave: Do First

| Priority | Source | Client | Signal | First touch | Owner | Destination | Why first |
|---|---|---|---|---|---|---|---|
| 1 | Gmail tender folder | B2B, companies | Tender/request for проектирование, РД, конструктив | Commercial reply, call, КП | Agent 2 + Agent 5 | Bitrix24 + manager task | Tender emails already arrive daily |
| 2 | Telegram chats | B2C + B2B | Person asks about перепланировка, проект, конструктив, согласование | Human-style reply after approval | Agent 6 + manager approval | Outreach queue -> Bitrix24 if interest | Code chain already exists |
| 3 | Profi.ru | B2C + small B2B | Client posts a job request | Paid response on platform | Manager / future collector | Bitrix24 | Worked before and gave clients |
| 4 | Yandex Services | B2C + small B2B | Client posts a job request | Response on platform | Manager / future collector | Bitrix24 | Worked before, lower start friction |
| 5 | Avito | B2C + B2B | Message to listing or relevant request | Reply inside Avito, then qualification | Agent 2 + Agent 4 | Bitrix24 | Listings already exist, demand was seen |
| 6 | Yandex Maps card | Local B2C/B2B | Search for company/service, call, message, route | Company card, phone, messenger, website | Agent 4 / manager | Bitrix24 manually at first | Card is not configured, so local demand is leaking |

## Second Wave: Add After First Contacts Work

| Source | Client | Signal | First touch | Why wave 2 |
|---|---|---|---|---|
| 2GIS card + 2GIS search | Local B2C/B2B, partners | Search by category, company discovery | Card, phone, message, website | Good for local trust and enrichment, but first fix Yandex Maps |
| VK groups | B2C | Questions in comments/groups | Helpful comment or DM after approval | Useful, but noisier than Telegram |
| Commercial tender platforms | B2B | Tender by project category | Formal response / platform bid | Strong, but needs source-by-source setup |
| HH.ru vacancies | B2B companies | Vacancy for architect, constructor, project engineer, fit-out manager | Careful B2B message to company | Signal of internal need or overload, but needs careful filtering |
| Partners: designers, builders, realtors | B2C + B2B | Partner has client before project stage | Partner referral | Strong quality, but relationship process must be created |
| Website / landing pages | All segments | Visitor wants proof, price, service path, lead magnet | Form, phone, messenger, bot | Needed for trust and tracking, but not before core positioning |

## Third Wave: Long-Term Sources

| Source | Client | Signal | First touch | Why later |
|---|---|---|---|---|
| EIS/government procurement | B2B/government | Procurement request | Formal tender participation | Important but heavy rules and lower startup priority |
| Developer procurement pages | Developers, networks | Supplier/project tender page updated | Email/procurement contact | Valuable, needs target account list |
| Franchise directories | Retail/franchise networks | New points, expansion | B2B email/intro | Warm signal, but slower cycle |
| Commercial real estate listings | Business owners, tenants | Buying/renting premises | Broker/business contact | Good signal, but harder attribution |
| Banks and mortgage brokers | B2C | Deal blocked by перепланировка | Partner referral | Strong but requires partnership |
| BTI/cadastral/legal partners | B2C | Client needs documents/legalization | Partner referral | Strong, relationship-based |
| Suppliers: kitchens, glazing, ventilation, signage | B2C/B2B | Client is changing premises | Partner referral | Good adjacent signal, needs partner offer |
| Forums and niche communities | B2C/B2B | Long discussion of renovation/project problems | Helpful public answer | Can work, but slow and noisy |

## Sources We Had Not Emphasized Enough

These are not all first-wave items, but they should stay in the system map.

| Missed / underweighted source | Why it matters | Recommended wave |
|---|---|---|
| Search demand: Yandex Search / SEO pages | People search exact services before asking in chats | 2 |
| Yandex Direct to narrow landing pages | Can bring hot traffic to service-specific pages | 2 |
| Retargeting from site visitors | People compare several studios before contacting | 3 |
| Developer and retail-chain procurement pages | Some companies publish tenders outside aggregators | 3 |
| NOPRIZ/SRO/professional network | B2B trust and partnerships, not mass leads | 3 |
| Commercial real estate brokers | They see clients before renovation/project work starts | 2 |
| Fit-out and signage contractors | They meet businesses opening or changing premises | 2 |
| Mortgage brokers and real estate lawyers | They see blocked сделки and перепланировка risks | 2 |
| Banks/insurance/valuation partners | They see problem cases around mortgage and documents | 3 |
| Facility management / управляющие компании | They see реконструкция and commercial maintenance needs | 2 |
| Reviews of competitors | Negative reviews can reveal unmet demand | 3 |
| Existing client base / past clients | Repeat projects and referrals are cheaper than new traffic | 1 |

## Lead Magnet Decision

Clear answer: yes, a lead magnet is needed, but not as the first technical dependency.

It should not replace direct lead collection. It should catch people who are not ready to call yet.

### Best Lead Magnets for This Project

| Lead magnet | Segment | First touch | Why it fits |
|---|---|---|---|
| "ПРОВЕРКА перепланировки" | B2C перепланировки | MAX / Telegram / website form | Already designed in `content/strategy/lead-intake-scenario.md` and matches urgent pain |
| "Проверка риска перед покупкой квартиры" | B2C buyers/sellers | Realtor, maps, website, posts | Tied to mortgage, deal, bank, EGRN pain |
| "Экспресс-разбор тендера / ТЗ" | B2B engineering | Email, tender flow, website | Converts tender traffic into structured КП action |
| "Чек-лист: какие документы нужны для РД/конструктива" | B2B | Website, Telegram, email | Warmer educational lead, not always hot |
| "Калькулятор предварительного диапазона стоимости" | B2C + B2B | Website/landing | Useful later, but risky if pricing is too rough |

### What Not To Do

- Do not make a generic PDF like "10 tips about project design" as the main lead magnet.
- Do not ask 15 questions on first contact.
- Do not hide the main contact path behind a long quiz.
- Do not build a large website before the first working lead path is tested.

## Website Decision

Clear answer: yes, a website or at least focused landing pages are needed.

But the first version should be small:

| Page | Purpose | Priority |
|---|---|---|
| Перепланировка под ключ | Convert B2C hot and warm traffic | 1 |
| Проверка перепланировки / риск сделки | Host lead magnet | 1 |
| Инженерное проектирование / РД / конструктив | Convert B2B traffic | 1 |
| Кейсы / команда / документы доверия | Trust proof for both flows | 1 |
| Контакты + формы + мессенджеры | Capture leads | 1 |

The site is not "for beauty". It is the receiving point for traffic from maps, content, direct ads, partner links, and lead magnets.

## Final First-Touch Sequence

We should move in this order:

1. Fill `.env` and authorize Telegram sessions.
2. Run the existing tender + Telegram MVP.
3. Configure Yandex Maps card because it is a current leak.
4. Reactivate Profi.ru and Yandex Services manually before automating them.
5. Build one lead magnet path: "ПРОВЕРКА перепланировки".
6. Build a small landing/site structure around the two service flows.
7. Add Avito collector and better content routing.

## Research Notes and Sources

- 2GIS Directory API supports searching organizations, buildings and places by field of activity, category, city and other parameters: https://dev.2gis.ru/en/api/catalog
- Yandex Business states that a filled organization card in Yandex Maps helps promote the business and attract clients, and that more complete cards rank better in Search and Maps: https://yard.yandex.ru/courses/yandex-karty-dlya-biznesa/zachem-nuzhny
- HeadHunter has an official API and OAuth model, making vacancy-based demand signals technically plausible: https://dev.hh.ru/
- B2B-Center has live tender pages for project-related requests and says companies can find procurement procedures and participate after registration/tariff selection: https://www.b2b-center.ru/search-tender/tendery-proektirovanie/
- HubSpot explains that lead generation forms turn visitors into leads and must be simple enough to create a good user experience: https://blog.hubspot.com/marketing/cta-vs-form-blog-conversion-test
- B2B website lead generation guidance recommends starting with one weak link, one relevant content offer, secondary CTAs and faster contextual follow-up instead of building everything at once: https://www.trajectorywebdesign.com/blog/b2b-website-lead-gen/
