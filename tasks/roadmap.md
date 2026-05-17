# Роадмап разработки Lead Intelligence Pipeline
## ООО «Вектор Плюс-Про» — дата: 2026-04-28

---

## Что уже работает (готовый код)

| Модуль | Файл | Статус |
|---|---|---|
| Инфраструктура shared/ | models, redis_client, db, logger | ✅ готово |
| Оркестратор | orchestrator/scheduler.py | ✅ готово |
| Конфиг + ключевые слова | config/settings.py | ✅ готово |
| Агент 2: тендерные письма через Email IMAP | agent2_collector/tender_collector | ✅ готово |
| Агент 3: дедупликация | agent3_processor/cleaner | ✅ готово |
| Агент 3: обогащение regex | agent3_processor/enricher | ✅ готово |
| Агент 3: скоринг Claude API | agent3_processor/scorer | ✅ готово |
| Агент 3: генерация оффера | agent3_processor/offer_gen | ✅ готово |
| Агент 3: склейка пайплайна | agent3_processor/__init__ | ✅ готово |
| Агент 5: Bitrix24 CRM | agent5_crm/bitrix | ✅ готово |
| Агент 5: TG-уведомления | agent5_crm/notifier | ✅ готово |
| Агент 5: CRM-роутер | agent5_crm/__init__ | ✅ готово |
| Агент 6: TG мониторинг | agent6_outreach/tg_monitor | ✅ готово |
| Агент 6: диалог по стадиям | agent6_outreach/sales_dialog | ✅ готово |
| Оркестратор | orchestrator/scheduler.py | ✅ готово |
| Redis blocklist | shared/redis_client.py | ✅ готово |

---

## Волна 1 — MVP (порядок строгий, зависимости важны)

### Шаг 1 — Агент 3: Процессор лидов ✅ ГОТОВО
Лиды копятся в Redis но никуда не движутся пока нет Агента 3.

| Субагент | Файл | Что делает |
|---|---|---|
| `cleaner` | agent3_processor/cleaner | Дедупликация по fingerprint (hash текста+контакта), фильтр нецелевых |
| `scorer` | agent3_processor/scorer | Claude API → hot/warm/cold/off + причина |
| `offer_gen` | agent3_processor/offer_gen | Claude API → персональный оффер + рекомендованное действие |
| `enricher` | agent3_processor/enricher | Извлечь город, тип объекта, площадь, контакт из raw_text |

**Порядок:** cleaner → enricher → scorer → offer_gen → push_qualified

---

### Шаг 2 — Агент 5: Уведомления менеджеру ✅ ГОТОВО

| Субагент | Файл | Что делает |
|---|---|---|
| `notifier` | agent5_crm/notifier | TG-уведомление: 🔥 горячий / ⚡ тёплый / 🤝 холодный + ссылка Bitrix |

---

### Шаг 3 — Агент 6: Полная цепочка аутрича ✅ ГОТОВО
tg_monitor → relevance → responder → approver → sender → lead_detector → Агент 5

| Субагент | Файл | Что делает |
|---|---|---|
| `relevance` | agent6_outreach/relevance | Claude Haiku → оценка 0–10, порог 7, до 10/цикл |
| `responder` | agent6_outreach/responder | Claude Sonnet → живой ответ от имени сотрудника ВПП |
| `approver` | agent6_outreach/approver | TG-бот daemon: ✅/✏️/❌, TTL 30 мин, Redis state |
| `sender` | agent6_outreach/sender | Telethon daemon: задержка 2–15 мин, дневной лимит |
| `lead_detector` | agent6_outreach/lead_detector | Haiku детектор интереса → OutreachLead → Агент 5 |

---

### Шаг 4 — Агент 2: Avito [средний приоритет]
Второй по важности источник лидов после тендеров.

| Субагент | Файл | Что делает |
|---|---|---|
| `avito_collector` | agent2_collector/avito_collector | Мониторинг поисковой выдачи Avito по ключевым словам, ротация UA |

---

### Шаг 5 — Агент 5: Управление и KP [средний приоритет]

| Субагент | Файл | Что делает |
|---|---|---|
| `admin_bot` | agent5_crm/admin_bot | TG-бот: /status /restart /stop /logs /pause |
| `proposal_trigger` | agent5_crm/proposal_trigger | Горячий лид → запуск KP-генератора (vpp_bot/) |

---

## Волна 2 — Расширение источников

| Субагент | Файл | Что делает |
|---|---|---|
| `profi_collector` | agent2_collector/profi_collector | Playwright сессия Profi.ru → заявки + автоотклик |
| `ya_uslugi_collector` | agent2_collector/ya_uslugi_collector | Заявки Яндекс Услуги (бесплатно до лимита) |
| `hh_collector` | agent2_collector/hh_collector | HH как B2B-разведка: вакансия «нужен конструктор» = компания имеет проект |
| `maps_collector` | agent2_collector/maps_collector | Входящие Яндекс Карты / 2GIS |
| `avito_poster` | agent4_publisher/avito_poster | Обновление объявлений Avito |
| `tg_poster` | agent4_publisher/tg_poster | Постинг в Telegram канал |
| `vk_poster` | agent4_publisher/vk_poster | Постинг в VK группу |
| `maps_poster` | agent4_publisher/maps_poster | Обновление карточки Яндекс Карты / 2GIS |
| `vk_monitor` | agent6_outreach/vk_monitor | vk_api мониторинг комментариев |
| `vk_hunter` | agent6_outreach/vk_hunter | Поиск по VK за период |
| `tg_hunter` | agent6_outreach/tg_hunter | Poиск по истории TG за 7–30 дней |
| `cold_email` | agent6_outreach/cold_email | B2B рассылка застройщикам с рабочего email |
| `content_pipeline` | agent4_publisher/content_pipeline | Конкуренты → Claude → адаптация под площадку |
| `dzen_poster` | agent4_publisher/dzen_poster | Статьи Яндекс Дзен (SEO, 1500–3000 слов) |
| `max_poster` | agent4_publisher/max_poster | Постинг в MAX + бот ПРОВЕРКА |
| `stats_reporter` | agent5_crm/stats_reporter | Еженедельный отчёт: источники, конверсия, потоки |

---

## Волна 3 — Продвинутые функции

| Субагент | Файл | Что делает |
|---|---|---|
| `youdo_collector` | agent2_collector/youdo_collector | Заявки YouDo (Поток А) |
| `property_signal` | agent2_collector/property_signal | ЦИАН/Авито Недвижимость: покупка = сигнал А |
| `avito_spy` | agent1_scout/avito_spy | Тексты и цены конкурентов на Avito |
| `maps_spy` | agent1_scout/maps_spy | Карточки конкурентов Яндекс Карты/2GIS |
| `review_monitor` | agent1_scout/review_monitor | Новые отзывы конкурентов → перехват |
| `tender_intel` | agent1_scout/tender_intel | Цены победителей тендеров → ценовая рекомендация |
| `forum_monitor` | agent6_outreach/forum_monitor | forumhouse.ru и аналоги |
| `forum_hunter` | agent6_outreach/forum_hunter | Поиск по форумам за месяц |
| `max_monitor` | agent6_outreach/max_monitor | Мониторинг соцсети Max |
| `tenchat_monitor` | agent6_outreach/tenchat_monitor | TenChat B2B застройщики/девелоперы |
| `tenchat_hunter` | agent6_outreach/tenchat_hunter | Поиск по TenChat |
| `yandex_q_monitor` | agent6_outreach/yandex_q_monitor | Вопросы про перепланировку Яндекс Кью |
| `ab_tester` | agent6_outreach/ab_tester | Фиксация каких тексты дали отклик |
| `boards_poster` | agent4_publisher/boards_poster | Региональные доски объявлений |

---

## Важное уточнение по Agent 4 Publisher

Agent 4 Publisher изначально назначался не только как технический постер, а как блок публикационных поверхностей и точек доверия, которые помогают лидогенерации.

Поэтому папки `agent4_publisher/avito_poster`, `boards_poster`, `content_pipeline`, `dzen_poster`, `maps_poster`, `max_poster`, `tg_poster`, `vk_poster` нужно оставить как roadmap-слоты будущих направлений, даже если часть рабочей реализации уже вынесена в новую структуру `core/` и `posters/`.

Текущее разделение ответственности:

- Agent 4 Publisher: публикации, объявления, карточки, контент, лендинги, точки доверия и события публикаций;
- Agent 2 Collector: сбор сырых лидов из источников;
- Agent 6 Outreach: первое касание, диалоги и детекция интереса;
- Agent 1 Scout / `source-radar`: разведка, конкуренты, тренды и внешние сигналы.

Правило: если канал реально внедряем, пустой roadmap-slot превращается в конкретный adapter/collector с контрактом, dry-run, approval и проверкой безопасности. Реальные публикации не запускать без отдельного подтверждения.

## Backlog после первого MVP — GEO/AI lead source

Статус: отложено. MVP-архитектуру не менять и новых агентов не создавать.

Подробные документы:

```text
tasks/geo-ai-lead-source-backlog.md
tasks/geo-ai-source-of-truth-next-step.md
docs/geo-ai-source-of-truth.md
```

Смысл слоя:

```text
AI-ответы / нейропоиск / поиск -> переход на сайт/карточку/статью -> лид -> CRM -> сделка -> ROMI
```

Подключать только после первого сквозного MVP:

```text
.env -> Redis -> Telegram-сессии -> Bitrix24 -> один тестовый лид
```

Ответственные внутри текущей системы:

| Блок | Кто отвечает |
|---|---|
| Проверка AI-ответов и конкурентов | Agent 1 Scout |
| Усиление сайта, кейсов, статей, карточек | Agent 4 Publisher |
| Учет AI/referrer traffic, сделок и ROMI | Agent 5 CRM/Analytics |

Текущий ручной аудит доведён до `Среза 6` в `research/geo-ai-visibility-audit.md`.

Следующий обязательный ручной шаг выполнен: создан `docs/geo-ai-source-of-truth.md`, чтобы зафиксировать единую публичную связку:

```text
ООО Вектор Плюс-Про -> ИНН/ОГРН -> сайт -> СРО -> услуги -> кейсы -> СИЛА Проекта
```

Важно: этот шаг не меняет MVP-архитектуру, не создаёт новых агентов и не означает публикацию без согласования.

Следующий маленький ручной шаг выполнен: подготовлен черновик блока `О компании` для сайта и канала `СИЛА Проекта`.

Файл:

```text
docs/about-company-and-channel-draft.md
```

Новый следующий маленький шаг уточнён: старый Bitrix24-сайт не использовать как будущую публичную ссылку; он остаётся только временным источником фактов.

Следующий маленький шаг: открыть локальный сайт из `site/` через `./OPEN_SITE.command` и визуально проверить шапку, первый экран, услуги, контакты и мобильную версию; структура, ТЗ и первая локальная версия сайта уже подготовлены.

---

## Параллельные задачи (НЕ код — руками)

| Задача | Кто | Зачем |
|---|---|---|
| Настроить точку Яндекс Карты | Яна | Теряем весь локальный поиск |
| Реактивировать Profi.ru | Яна | Откликаться на заявки (платно за отклик) |
| Реактивировать Яндекс Услуги | Яна | Бесплатно до лимита, давали клиентов |
| Прогрев TG-аккаунта для Агента 6 | Сергей | 2–4 недели до начала аутрича |
| Создать пароль приложения Яндекс.Почты | Яна | Нужен для tender_collector через IMAP |
| Webhook Bitrix24 | Яна | Нужен для agent5_crm/bitrix |

---

## Критические правила системы

- **Approver** должен работать всегда. Нет ответа 30 мин → лид НЕ отправляется + алерт
- **Claude API hard cap** токенов в оркестраторе. 80% → алерт, 100% → стоп всех Claude-вызовов
- **Redis AOF persistence** включён. Без этого потеря лидов при перезапуске
- **Blocklist** конкуренты/боты → shared/redis_client.py. Проверка на входе в Агент 2
- **Контент**: разные каналы = разный угол. Не копировать MAX в TG без адаптации

---

## Следующая сессия: начинаем с Агента 3

```
Файлы для написания (в порядке):
1. agents/agent3_processor/cleaner/__init__.py
2. agents/agent3_processor/enricher/__init__.py
3. agents/agent3_processor/scorer/__init__.py
4. agents/agent3_processor/offer_gen/__init__.py
5. agents/agent3_processor/__init__.py  ← склейка всех четырёх
6. agents/agent5_crm/notifier/__init__.py
```

После этого первый сквозной тест:
tender_collector → Redis → Агент 3 → Bitrix24 → TG-уведомление менеджеру
